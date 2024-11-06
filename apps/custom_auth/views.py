import datetime, jwt, random, pytz, logging
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.utils.six import text_type
from django.shortcuts import render
from django.contrib.auth import views as auth_views
import requests
import json
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.state import token_backend
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import generics, status
from rest_framework.views import APIView
from apps.user.models import User, UserDeviceToken
from apps.custom_auth.models import PasswordResetOtp
from yellowsquash import env_constants
from apps.common_utils.MobileOtp import Otp
from apps.tinode.tinode import Tinode

logger = logging.getLogger(__name__)

# 13 for around 3 months
TOKEN_LIFETIME = datetime.timedelta(weeks=13)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):


        error_message = None
        
        # user can login via email also if we got any user with matching email or mobile number then with 
        # username and no user exit with same user name then update object
        if not User.objects.filter(username=attrs.get('username')).exists():
            if User.objects.filter(email=attrs.get('username')).exists():
                attrs['username'] = User.objects.filter(email=attrs.get('username')).first().username
            if User.objects.filter(mobile=attrs.get('username')).exists():
                attrs['username'] = User.objects.filter(mobile=attrs.get('username')).first().username


        # validate before processing
        if not User.objects.filter(username=attrs.get('username')).exists():
            error_message = "Invalid Username : Requested User Doesn't Exist"
        elif not User.objects.filter(username=attrs.get('username')).first().check_password(attrs.get('password')):
            error_message = "Incorrect Password"
        elif self.initial_data and 'user_type' in self.initial_data :
            user_type = User.objects.filter(username=attrs.get('username')).first().user_type
            if self.initial_data.get('user_type') != user_type :
                error_message = "This user is registered with Yellow Squash as {0}. Please download {0} App".format(user_type)

        # if there is error in validation stop processing
        if error_message:
            raise exceptions.AuthenticationFailed(
                error_message
            )


        ## This data variable will contain refresh and access tokens
        data = super().validate(attrs)

        # upadte token life
        refresh = self.get_token(self.user)
        data['refresh'] = text_type(refresh)
        new_token = refresh.access_token
        new_token.set_exp(lifetime=TOKEN_LIFETIME)
        data['access'] = text_type(new_token)
        

        # update token data and set token in response
        tokenData = token_backend.decode(data['access'], verify=True)
        tokenData['username'] = self.user.username
        tokenData['tinode_token'] = self.user.tinode_token
        data['access'] = token_backend.encode(tokenData)

        # checking user have tinode token 
        if(self.user.tinode_token is None):
            try:
                tinodeNew = Tinode()
                token = tinodeNew.CreateUserAndGetToken(
                    username=self.user.username,
                    password=attrs.get('password'),
                    first_name=self.user.first_name if self.user.first_name else "User",
                    tags=[self.user.user_type if self.user.user_type else 'customer'],
                )
                if token:
                    logger.info(token)
                    self.user.tinode_token = token
                    self.user.save()
                else:
                    logger.info(
                        "tinode token genration failed for the username : ",attrs.get('username'))
            except BaseException as err:
                logger.exception(
                    "Failed getting tinode token : ", exc_info=err)

        # make and add jitsi token 
        jitsi_token_payload = {
            "user": {
                "avatar": "",
                "name": self.user.first_name,
                "id": self.user.id
            },
            "aud": "jitsi",
            "iss": env_constants.getJitsiIss(),
            "sub": env_constants.getJitsiSub(),
            "room": "*",
            "moderator": self.user.user_type == 'expert'
        }
        jitsi_token = jwt.encode(jitsi_token_payload,
                                env_constants.getJitsiPasswordSecret(), algorithm='HS256')

        # if user device token available then save it
        try:
            if self.initial_data and 'device_token' in self.initial_data :
                userDeviceToken = UserDeviceToken.objects.get_or_create(
                    user_id = self.user.id,
                    device_token = self.initial_data.get('device_token'),
                    defaults={
                        'user_id': self.user.id,
                        'device_token': self.initial_data.get('device_token')
                    }
                )
        except BaseException as err:
            print(err)

        ## You can add more User model's attributes like username,email etc. in the data dictionary like this.
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['mobile'] = self.user.mobile
        data['title'] = self.user.title
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['nick_name'] = self.user.nick_name
        data['user_type'] = self.user.user_type
        data['biographic_info'] = self.user.biographic_info
        data['user_img'] = self.user.user_img
        data['tinode_token'] = self.user.tinode_token
        data['qualification'] = self.user.qualification
        data['experience'] = self.user.experience
        #data['expertise'] = self.user.experties
        data['expertise'] = list(self.user.experties.all().values())
        data['jitsi_token'] = jitsi_token
        data['status'] = self.user.status
        data['is_profile_complete'] = self.user.is_profile_complete

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# send 6 digit otp for forgot password
class ForgotPassword(generics.CreateAPIView):

    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        sendOtp = Otp()
        try:
            otp = random.randint(100000, 999999)
            user = None
            error_message = None

            # validate request
            # user can request forgot passward with email/mobile or username
            # username and no user exit with same user name then try fetching data considering username as email
            if 'username' not in request.data and not request.data.get('username'):
                error_message = "Incomplete Request : forgot password can't be requested with username"
            # elif 'user_type' not in request.data and not request.data.get('user_type'):
            #     error_message = "Incomplete Request : forgot password can't be requested with user_type"
            elif not User.objects.filter(username=request.data.get('username')).exists():
                if User.objects.filter(email=request.data.get('username')).exists():
                    user = User.objects.filter(email=request.data.get('username')).first()
                elif User.objects.filter(mobile=request.data.get('username')).exists():
                    attrs['username'] = User.objects.filter(mobile=request.data.get('username')).first().username
                else:
                    error_message = "No Active Account have username/email/mobile : {0}".format(request.data.get('username'))
            else:
                user = User.objects.filter(username=request.data.get('username')).first()
            # if not error_message and user.user_type != request.data.get('user_type'):
            #     error_message = "Incorrect user_type field value"

            # if there is validation error then stop process
            if error_message:
                return JsonResponse({
                    'message': error_message
                    }, 
                    safe=False, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


            PasswordResetOtp.objects.update_or_create(
                user=user, defaults={'otp': otp},
            )

            # sending mobile otp
            try:
                data = sendOtp.MobileOtp(user.mobile,otp)
            except BaseException as err:
                print(err)

            #sending email otp
            # try:
            #     task={
            #         "sender":{
            #             "name":"YellowSquash",
            #             "email":"yellowsquash@gmail.com"
            #         },
            #         "to":[
            #             {
            #                 "email":"{0}".format(user.email),
            #                 "name":"yellowsquash"
            #             }
            #         ],
            #         "templateId":94,
            #         "params":{"name":"sandeep","otp":"{0}".format(otp)}
            #     }
            #     sendOtp.EmailOtp(task)
            # except BaseException as err:
            #     print(err)


            #sending mail
            mailSendRes = send_mail(
                subject = 'FORGOT PASSWORD',
                message = '',
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [user.email,],
                html_message="""<!DOCTYPE html>
                <html>
                <body>
                    <p>Dear User,</p>
                    <p>We have sent you this email in response to your request to reset your password.</p>
                    <p>We recommend that you keep your password secure and not share it with anyone.If you feel your password has been compromised, you can change it from your mobile application.</p>
                    <p>Please Don't share your opt with anyone.</p>
                    <p>OTP : <b>{0}</b></p>
                </body>
                </html>""".format(otp),
                fail_silently=True
            )

            # if mailSendRes != 1:
            #     print("error while semding otp on mail address")

            return JsonResponse({"message": "success"}, status=status.HTTP_202_ACCEPTED)

        except BaseException as err:
            print(err)
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class VerifyOtp(generics.CreateAPIView):

    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            # validate request 
            if 'otp' not in request.data:
                return JsonResponse({
                        'message': "mandatory data otp missing in request"
                    }, 
                    safe=False, 
                    status=status.HTTP_400_BAD_REQUEST
                )


            if not PasswordResetOtp.objects.filter(otp=request.data.get('otp')).exists():
                return JsonResponse({
                        'message': "OTP doesn't exist, Please try again!"
                    }, 
                    safe=False, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # on otp verification please get user an access token like given on login
            access_token_payload = {
                "token_type": "access",
                "user_id": PasswordResetOtp.objects.filter(otp=request.data.get('otp')).first().user.id,
            }
            access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
            
            # update token in table for further verification
            optObj = PasswordResetOtp.objects.filter(otp=request.data.get('otp')).first()
            optObj.token = access_token
            optObj.otp = ""
            optObj.save()

            return JsonResponse({
                    "message": "success",
                    "token": access_token
                }, 
                status=status.HTTP_202_ACCEPTED)

        except BaseException as err:
            print(err)
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ResetForgotPassword(generics.CreateAPIView):

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            # authenticate data and update password
            if 'token' in request.data and PasswordResetOtp.objects.filter(token = request.data.get('token')).exists():
                user = PasswordResetOtp.objects.filter(token = request.data.get('token')).first().user
                user.set_password(request.data.get('new_password'))
                user.save()
                PasswordResetOtp.objects.filter(token = request.data.get('token')).first().delete()
            else:
                return JsonResponse({
                        'message': "token expired or already used"
                    }, 
                    safe=False, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # get new user token and give it in response
            serializer = self.get_serializer(data={
                'username': user.username,
                'user_type': user.user_type,
                'password': request.data.get('new_password'),
            })

            serializer.is_valid(raise_exception=True)
            try:
                task={  
                    "sender":{  
                        "name":"YellowSquash",
                        "email":"yellowsquash@gmail.com"
                    },
                    "to":[  
                        {  
                            "email":"sandeep@opskube.com",
                            "name":"sandeep"
                        }
                    ],
                    "templateId":27,
                    "params":{"name":"sandeep"}
                }
                sendOtp.EmailOtp(task)
            except BaseException as err:
                print(err)

            return JsonResponse(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        except BaseException as err:
            print(err)
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ResetPassword(generics.CreateAPIView):

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            error_message = ''
            # authenticate data
            if 'old_password' in request.data :
                if not request.user.check_password(request.data.get('old_password')):
                    error_message = 'incorrect old password'
            else:
                error_message = "mandatory field old password missing"

            # if error stop processing
            if error_message:
                return JsonResponse({
                        'message': error_message
                    }, 
                    safe=False, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # update password
            if 'new_password' in request.data :
                user = request.user
                user.set_password(request.data.get('new_password'))
                user.save()
            else:
                return JsonResponse({
                        'message': "mandatory field new password missing"
                    }, 
                    safe=False, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # get new user token and give it in response
            serializer = self.get_serializer(data={
                'username': user.username,
                'user_type': user.user_type,
                'password': request.data.get('new_password'),
            })

            serializer.is_valid(raise_exception=True)

            return JsonResponse(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        except BaseException as err:
            print(err)
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




''' 
this api will be use when ananymous user subscribed program 
And After payment success when ananymous user will try to 
reset password.
 '''
class GetUpdatePasswordToken(APIView):
    permission_classes = (AllowAny,)

    def post(self,request):
        otp = random.randint(100000, 999999)
        try:
            user = User.objects.get(id=int(request.data["user_id"]))
            access_token_payload = {
            "token_type": "access",
            "user_id": user.id
            }

            PasswordResetOtp.objects.update_or_create(
                                    user=user, defaults={'otp': otp},
                                    )
            access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
            optObj = PasswordResetOtp.objects.filter(otp=otp).first()

            optObj.token = access_token
            optObj.save()
            
            return JsonResponse({
                "message": "success",
                "token": access_token
                }, 
                status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "error":"user not exists",
            },status=404)

        except ValueError:
            return Response({
                "error":"Invalid user id given"
            },status=400)


        except BaseException as err:
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





