import json
import random
import string
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from rest_framework import generics, status, views, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import authentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import *
from apps.program.models import Discount
from .serializer import *
from apps.custom_auth.views import CustomTokenObtainPairSerializer
from apps.program.models import Program, ProgramBatch
from apps.program.serializer import ProgramBatchUserSerializer, GlobalSearchProgramSerializer
from apps.tinode.tinode import Tinode
from yellowsquash import env_constants
from apps.blog.models import Blog
from apps.blog.serializers import BlogListSerializer, GlobalSearchBlogSerializer
from django.utils.six import text_type
import datetime
import logging
import razorpay
from apps.common_utils.MobileOtp import Otp

from apps.common_utils.Aws import Aws, AwsFilePath

from PIL import Image

from ..common_utils.standard_response import success_response, error_response

logger = logging.getLogger(__name__)

razorpay_client = razorpay.Client(
    auth=(env_constants.getRazorpayKey(), env_constants.getRazorpaySecret()))


class SendEmailVerificationOtp(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        sendOtp = Otp()
        try:
            otp = random.randint(100000, 999999)
            randomGeneratedPassword = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(12))
            print("its working")
            # create user or get user
            isEmail = False
            if ("@" in request.data.get("email")):
                isEmail = True

            if isEmail and User.objects.filter(email=request.data.get('email')).exists():

                if User.objects.get(email=request.data.get('email')).is_verified:
                    return JsonResponse({
                        'message': 'User is already registered with the requested email address'
                    }, status=status.HTTP_400_BAD_REQUEST)

                user = User.objects.get(email=request.data.get('email'))

            elif (not isEmail and (User.objects.filter(mobile=request.data.get("email"))).exists()):

                if User.objects.filter(mobile=request.data.get('email')).first().is_verified:
                    return JsonResponse({
                        'message': 'User is already registered with the requested Mobile Number'
                    }, status=status.HTTP_400_BAD_REQUEST)

                user = User.objects.get(mobile=request.data.get('email'))

            else:
                groupd, is_created = Group.objects.get_or_create(
                    defaults={'name': "Default User Group"}
                )
                if (isEmail):
                    # creating user with given email id
                    user = User.objects.create(
                        username=request.data.get('email'),
                        email=request.data.get('email'),
                        user_type='customer',
                        group=groupd,
                        user_img=None
                    )
                else:
                    # creating user with given mobile number

                    user = User.objects.create(
                        username=request.data.get('email'),
                        mobile=request.data.get('email'),
                        user_type='customer',
                        group=groupd,
                        user_img=None
                    )

            user.set_password(randomGeneratedPassword)
            user.save()

            # update old object if already exist no user can have multiple otp in once
            if VerifyOtp.objects.filter(user=user).exists():
                verifyOtp = VerifyOtp.objects.get(user=user)
                verifyOtp.otp = otp
                verifyOtp.save()
            else:
                VerifyOtp.objects.create(
                    user=user,
                    otp=otp,
                )

            # sending sendinblue email
            # task = {
            #     "sender": {
            #         "name": "YellowSquash",
            #         "email": "yellowsquash@gmail.com"
            #     },
            #     "to": [
            #         {
            #             "email": "{0}".format(user.email),
            #             "name": "{0}".format(user.first_name)
            #         }
            #     ],
            #     "templateId": 73,
            #     "params": {"otp": "{0}".format(otp)}
            # }
            # if (isEmail):
            #     sendOtp.EmailOtp(task)
            # else:
            #     mobile = request.data.get("email")
            #
            #     sendOtp.MobileOtp(mobile, otp)

            # sending mail
            mailSendRes = send_mail(
                subject='Yellowsquash : Email Verification',
                message='',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email, ],
                html_message="""<!DOCTYPE html>
                <html>
                <body>
                    <p>Dear User,</p>
                    <p>We have sent you this email in response to your request to verify your email.</p>
                    <p>Please Don't share your opt with anyone.</p>
                    <p>OTP : <b>{0}</b></p>
                </body>
                </html>""".format(otp),
                fail_silently=True
            )

            # get login token and give it ot user
            loginSerializer = CustomTokenObtainPairSerializer(data={
                'username': request.data.get('email'),
                'password': randomGeneratedPassword,
                'device_token': request.data.get('device_token', None)
            })
            loginSerializer.is_valid(raise_exception=True)

            return JsonResponse({
                'message': 'Verification Mail Sent on mail address!' if isEmail else 'Verification Otp Sent on Mobile',
                'access': loginSerializer.validated_data.get('access')
            }, status=status.HTTP_201_CREATED)
        except BaseException as err:
            logger.exception("failed creating user : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailOtp(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            otp = request.data.get('otp')

            randomGeneratedPassword = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(12))

            if VerifyOtp.objects.filter(user=user, otp=otp).exists():
                VerifyOtp.objects.filter(user=user, otp=otp).delete()
            else:
                return JsonResponse({
                    'message': 'Please check your Otp and try again!'
                }, status=status.HTTP_400_BAD_REQUEST)
            if (user.email):
                user.email_verified = True
            else:
                user.mobile_verified = True

            user.set_password(randomGeneratedPassword)
            user.save()

            return JsonResponse({
                'message': 'Email Verified ! Please complete your signup now!' if user.email else "Mobile Verified ! Please Complete Your Signup"
            }, status=status.HTTP_201_CREATED)
        except BaseException as err:
            logger.exception(
                "failed verifying user mobile/email : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompleteSignup(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        sendOtp = Otp()
        try:

            if User.objects.filter(username=request.data.get('username')).exists():
                return JsonResponse({
                    'message': 'Username already exists',
                    'error': ''
                },
                    safe=False,
                    status=status.HTTP_400_BAD_REQUEST
                )

            else:

                '''
                checking user verified  with email otp or with mobile otp 
                if user verified with mobile otp so we need check provided email 
                is already registred or not
                '''

                verifiedUser = User.objects.get(id=request.user.id)
                if (verifiedUser.mobile_verified and not verifiedUser.email_verified):
                    if User.objects.filter(email=request.data.get('email')).exists():
                        return JsonResponse({
                            'message': 'Email Already Taken',
                            'error': ''
                        },
                            safe=False,
                            status=status.HTTP_400_BAD_REQUEST
                        )

                if (verifiedUser.email_verified and not verifiedUser.mobile_verified):
                    if User.objects.filter(mobile=request.data.get('mobile')).exists():
                        return JsonResponse({
                            'message': 'Mobile Number Already Taken',
                            'error': ''
                        },
                            safe=False,
                            status=status.HTTP_400_BAD_REQUEST
                        )

                user = request.user
                user.is_verified = True
                user.username = request.data.get('username')
                user.first_name = request.data.get('first_name')
                user.last_name = request.data.get('last_name')

                user.user_type = request.data.get('user_type', 'customer')
                user.set_password(request.data.get('password'))

                if request.data.__contains__('profile_picture'):
                    user.profile_picture = request.data['profile_picture']

                # new fields added
                if request.data.__contains__('nick_name'):
                    user.nick_name = request.data.get('nick_name')

                if request.data.__contains__('professional_title'):
                    user.professional_title = request.data.get('professional_title')

                if request.data.__contains__('short_description'):
                    user.short_description = request.data.get('short_description')

                if request.data.__contains__('location'):
                    user.location = Location.objects.get(pk=request.data.get('location'))

                if request.data.__contains__('timezone'):
                    user.timezone = TimeZone.objects.get(pk=request.data.get('timezone'))

                if request.data.__contains__('language'):
                    language_list = json.loads(request.data.get('language'))
                    languages = Languages.objects.filter(pk__in=language_list)
                    user.language.set(languages)

                if request.data.__contains__('expertise'):
                    if request.data.get('expertise'):
                        expertise_list = json.loads(request.data.get('expertise'))
                        expertises = Expertise.objects.filter(pk__in=expertise_list)
                        user.experties.set(expertises)

                # if not verifiedUser.mobile_verified and verifiedUser.mobile_verified is None:
                #     user.mobile = request.data.get('mobile')

                user.mobile = request.data.get('mobile')

                if not verifiedUser.email_verified and verifiedUser.email is None:
                    user.email = request.data.get("email")

                if request.data.get('user_type') == "expert":
                    user.status = 'inactive'
                user.save()

            # insert chat token if available
            try:
                tinodeNew = Tinode()
                token = tinodeNew.CreateUserAndGetToken(
                    username=request.data.get('username'),
                    password=request.data.get('password'),
                    first_name=request.data.get(
                        "first_name", "User"),  # can't be blank or null
                    # can't be blank or null
                    tags=[request.data.get("user_type", "customer")],
                )
                if token:
                    logger.info(token)
                    user.tinode_token = token
                    user.save()
                else:
                    logger.info(
                        "tinode token genration failed for the username : ", request.data.get('username'))
            except BaseException as err:
                logger.exception(
                    "Failed getting tinode token : ", exc_info=err)

            # get login token and give it ot user
            loginSerializer = CustomTokenObtainPairSerializer(data={
                'username': request.data.get('username'),
                'password': request.data.get('password')
            })

            loginSerializer.is_valid(raise_exception=True)
            try:
                if request.data['user_type'] != 'customer':
                    templateId = None
                    if (request.data['user_type'] == "expert"):
                        # templateId = 28
                        # task = {
                        #     "sender": {
                        #         "name": "YellowSquash",
                        #         "email": "yellowsquash@gmail.com"
                        #     },
                        #     "to": [
                        #         {
                        #             "email": "{0}".format(user.email),
                        #             "name": "{0}".format(user.first_name)
                        #         }
                        #     ],
                        #     "templateId": templateId,
                        #     "params": {"firstname": "{0}".format(user.first_name)}
                        # }
                        # sendOtp.EmailOtp(task)

                        # sending mail
                        mailSendRes = send_mail(
                            subject='Yellowsquash : Email Verification',
                            message='',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[user.email, ],
                            html_message="""<!DOCTYPE html>
                                        <html>
                                        <body>
                                            <p>Dear User,</p>
                                            <p>We have sent you this email in response to your request to verify your email.</p>
                                            <p>Please Don't share your opt with anyone.</p>
                                            <p>OTP : <b>{0}</b></p>
                                        </body>
                                        </html>""".format(user.first_name),
                            fail_silently=True
                        )

                    if (request.data['user_type'] == "expert"):
                        # templateId = 37
                        # task = {
                        #     "sender": {
                        #
                        #         "name": "YellowSquash",
                        #         "email": "yellowsquash@gmail.com"
                        #     },
                        #     "to": [
                        #         {
                        #             "email": "info@yellowsquash.in",
                        #             "name": "yellowsquash"
                        #         }
                        #     ],
                        #     "templateId": templateId,
                        # }
                        # sendOtp.EmailOtp(task)

                        # sending mail
                        mailSendRes = send_mail(
                            subject='Yellowsquash : Email Verification',
                            message='',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[user.email, ],
                            html_message="""<!DOCTYPE html>
                                            <html>
                                            <body>
                                                <p>Dear User,</p>
                                                <p>We have sent you this email in response to your request to verify your email.</p>
                                                <p>Please Don't share your opt with anyone.</p>
                                                <p>OTP : <b>{0}</b></p>
                                            </body>
                                            </html>""".format(user.first_name),
                            fail_silently=True
                        )

                else:
                    print("not")
            except BaseException as err:
                print(err, "====")
                print(loginSerializer.validated_data, "=============vd")
            return JsonResponse(loginSerializer.validated_data, status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            print(err, "===========")
            logger.exception(
                "Error Occured While Updating User Details : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            logger.info(json.dumps(request.data))

            # create user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            # get login token and give it ot user
            loginSerializer = CustomTokenObtainPairSerializer(data={
                'username': request.data.get('username'),
                'user_type': serializer.data.get('user_type'),
                'password': request.data.get('password'),
                'device_token': request.data.get('device_token', None)
            })
            loginSerializer.is_valid(raise_exception=True)

            return JsonResponse(loginSerializer.validated_data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            logger.exception("failed creating user : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SocialMediaAuth(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        validationErrorMessage = ""
        errorMessage = ""
        randomGeneratedPassword = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(8))

        # validate request for mandatory data
        if 'social_id' not in request.data or not request.data.get('social_id'):
            validationErrorMessage = "Mandatory Field social_id not recieved can't process your request"
        elif not User.objects.filter(username=request.data.get('social_id')).exists() and (
                'email' not in request.data or not request.data.get('email')):
            # for required filed email missing ask with status code 406
            validationErrorMessage = "Email is mandatory for our systmem please upadte email manually !"
            return JsonResponse({'message': validationErrorMessage}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not User.objects.filter(username=request.data.get('social_id')).exists() and User.objects.filter(
                email=request.data.get('email')).exists():

            user = User.objects.get(email=request.data.get('email'))
            serializer = self.get_serializer(user, many=False)
            data = dict()

            TOKEN_LIFETIME = datetime.timedelta(weeks=13)
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            data['refresh'] = text_type(refresh)
            new_token = refresh.access_token
            new_token.set_exp(lifetime=TOKEN_LIFETIME)
            data['access'] = text_type(new_token)
            serializer_data = serializer.data
            serializer_data["access"] = data["access"]

            return Response(serializer_data)
        if validationErrorMessage:
            return JsonResponse({'message': validationErrorMessage}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=request.data.get('social_id')).exists():
            user = User.objects.get(username=request.data.get('social_id'))
            user.set_password(randomGeneratedPassword)
            if (request.data.get('login_source') == 'facebook'):
                user.user_img = 'https://graph.facebook.com/{0}/picture?type=large'.format(
                    request.data.get('social_id'))
            user.save()
        else:
            # split full name into first name and last name
            name = request.data.get('name', "")
            first_name = name.split(' ')[0]
            last_name = ' '.join(name.split(' ')[1:])
            user_img = ''
            if (request.data.get('login_source') == 'facebook'):
                user_img = 'https://graph.facebook.com/{0}/picture?type=large'.format(
                    request.data.get('social_id'))
            serializer = self.get_serializer(data={
                'email': request.data.get('email'),
                'username': request.data.get('social_id'),
                'first_name': first_name,
                'last_name': last_name,
                'user_type': request.data.get("user_type", "customer"),
                'user_img': user_img,
                'password': randomGeneratedPassword,
            })
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            user = User.objects.get(username=request.data.get('social_id'))

        # get login token and give it ot user
        loginSerializer = CustomTokenObtainPairSerializer(data={
            'username': user.username,
            'user_type': request.data.get("user_type", "customer"),
            'password': randomGeneratedPassword,
            'device_token': request.data.get('device_token', None),
        })
        loginSerializer.is_valid(raise_exception=True)

        return JsonResponse(loginSerializer.validated_data, status=status.HTTP_201_CREATED)


class UpdateUser(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        aws = Aws()
        try:

            user = User.objects.get(id=request.user.id)

            user.email = request.data.get('email')
            user.first_name = request.data.get('first_name')
            user.last_name = request.data.get('last_name')
            user.mobile = request.data.get('mobile')
            user.title = request.data.get('title')
            user.nick_name = request.data.get('nick_name')
            # user.biographic_info = request.data.get('biographic_info')
            user.status = request.data.get('status')
            user.designation = request.data.get('designation')
            user.qualification = request.data.get('qualification')
            user.experience = request.data.get('experience')
            user.experties = request.data.get('experties')
            user.fb_link = request.data.get('fb_link')
            user.twitter_link = request.data.get('twitter_link')
            user.linked_link = request.data.get('linked_link')
            user.google_link = request.data.get('google_link')
            user.short_description = request.data.get('short_description')
            if request.FILES and 'file' in request.FILES and request.FILES['file']:
                userProfilePath = AwsFilePath.userProfilePath(
                    user_id=request.user.id,
                    resource_file_name=request.FILES['file'].name
                )
                user.user_img = aws.upload_file(
                    request.FILES['file'], userProfilePath)
            user.save()

            serializer = UserSerializer(user, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception(
                "Error Occured While Uodating User Details : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUserBasicDetails(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        aws = Aws()
        try:
            user = request.user
            if request.data.__contains__("mobile"):
                if User.objects.filter(mobile=request.data.get('mobile')).exists():
                    return JsonResponse({
                        'message': 'Mobile Number Already Taken',
                        'error': ''
                    },
                        safe=False,
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if request.data.__contains__("first_name"):
                user.first_name = request.data["first_name"]

            if request.data.__contains__("last_name"):
                user.last_name = request.data["last_name"]

            if request.data.__contains__("mobile"):
                user.mobile = request.data["mobile"]

            if request.data.__contains__("email"):
                user.email = request.data['email']

            if request.data.__contains__('profile_picture') and request.data['profile_picture']:
                user.profile_picture = request.data['profile_picture']

            # user.language = request.data.get('language', 'english')
            # user.location = request.data.get('location', '')

            if 'professional_title' in request.data:
                user.professional_title = request.data.get('professional_title', '')

            user.video_url = request.data.get('video_url', '')

            if 'short_description' in request.data:
                user.short_description = request.data.get('short_description', '')

            # user.biographic_info = request.data.get('biographic_info', '')
            if "location" in request.data:
                if request.data['location']:
                    user.location = Location.objects.get(pk=request.data.get('location'))
                else:
                    user.location = None

            if "timezone" in request.data:
                if request.data['timezone']:
                    user.timezone = TimeZone.objects.get(pk=request.data.get('timezone'))
                else:
                    user.timezone = None

            if request.data.__contains__("language"):
                language_list = json.loads(request.data.get('language'))
                languages = Languages.objects.filter(pk__in=language_list)
                user.language.set(languages)

            if request.data.get('expertise'):
                expertise_list = json.loads(request.data.get('expertise'))
                expertises = Expertise.objects.filter(pk__in=expertise_list)
                user.experties.set(expertises)

            user.age = request.data.get('age', user.age)
            user.gender = request.data.get('gender', user.gender)

            if 'interests' in request.data:
                interests_list = request.data.get('interests')
                interests = Category.objects.filter(id__in=interests_list)
                user.category.set(interests)

            user.save()

            if request.FILES and 'file' in request.FILES and request.FILES['file']:
                userProfilePath = AwsFilePath.userProfilePath(
                    user_id=request.user.id,
                    resource_file_name=request.FILES['file'].name
                )
                user.user_img = aws.upload_file(
                    request.FILES['file'], userProfilePath)
                user.save()

            serializer = UserSerializer(user, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception(
                "Error Occured While Uodating User Details : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileCompleted(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        aws = Aws()
        try:
            user = request.user

            user.is_profile_complete = True
            user.save()

            serializer = UserSerializer(user, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception(
                "Error Occured While Updating User Details : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetMyEducationDetails(generics.ListAPIView):
    serializer_class = UserEducationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserEducationDetail.objects.filter(user=self.request.user)


class AddUserEducation(generics.CreateAPIView):
    serializer_class = UserEducationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:

            serializer = self.get_serializer(data={
                'user': request.user.id,
                'course_name': request.data.get('course_name'),
                'institution_name': request.data.get('institution_name'),
                'completion_year': request.data.get('completion_year'),
                'description': request.data.get('description', ""),
                'certificate_doc': request.data.get('certificate_doc'),
            })
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception(
                "Error Occured While Uodating User Details : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUserEducation(generics.UpdateAPIView):
    serializer_class = UserEducationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, education_id):
        try:
            if UserEducationDetail.objects.filter(id=education_id, user=request.user.id).exists():
                userEducationDetail = UserEducationDetail.objects.get(
                    id=education_id, user=request.user.id)
            else:
                return JsonResponse({
                    'message': "No Education Detail Exist With Reuqested data!"
                }, status=status.HTTP_400_BAD_REQUEST)

            if 'course_name' in request.data and request.data.get('course_name'):
                # userEducationDetail.course_name = request.data.get(
                #     'course_name')
                course_name = DegreeCertification.objects.get(degree_id=request.data.get(
                    'course_name'))
                userEducationDetail.course_name = course_name

            if 'institution_name' in request.data:
                userEducationDetail.institution_name = request.data.get(
                    'institution_name')

            if 'completion_year' in request.data:
                userEducationDetail.completion_year = request.data.get(
                    'completion_year')

            if 'description' in request.data:
                userEducationDetail.description = request.data.get(
                    'description')

            if 'certificate_doc' in request.data and request.data.get('certificate_doc') != '' and request.data.get(
                    'certificate_doc') != 'null':
                userEducationDetail.certificate_doc = request.data.get(
                    'certificate_doc')

            userEducationDetail.save()
            serializer = self.get_serializer(userEducationDetail, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except BaseException as err:
            logger.exception(
                "Error Occured While Updating User Details : ", exc_info=err)
            errorRes = str(err)
            if "duplicate key value violates unique constraint" in str(err):
                errorRes = 'Duplicate Degree, {0} is already added.'.format(
                    request.data.get('course_name', None))
            return JsonResponse({
                'message': errorRes,
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteUserEducation(generics.DestroyAPIView):
    serializer_class = UserEducationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, education_id):
        try:
            if UserEducationDetail.objects.filter(id=education_id, user=request.user.id).exists():
                userEducationDetail = UserEducationDetail.objects.get(
                    id=education_id, user=request.user.id)
            else:
                return JsonResponse({
                    'message': "No Education Detail Exist With Reuqested data!"
                }, status=status.HTTP_400_BAD_REQUEST)

            userEducationDetail.delete()

            return JsonResponse({
                'message': 'success'
            }, status=status.HTTP_200_OK)
        except BaseException as err:
            logger.exception(
                "Error Occured While Updating User Details : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserList(generics.ListAPIView):
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @never_cache
    # get user all info
    def get(self, request):
        queryset = User.objects.filter(id=request.user.id)
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)


class ExpertListApi(generics.ListAPIView):
    permission_classes = (AllowAny,)

    # get user all info
    @never_cache
    def get(self, request):
        limit = 20
        offSet = 0
        setLimit = request.GET.get('limit', limit)
        setOfSet = request.GET.get('offset', offSet)
        if setLimit:
            limit = int(setLimit)
        if setOfSet:
            offSet = int(setOfSet)

        queryset = ExpertList.objects.raw('''
        select uu.id, uu.*, id,
        ( case
            when EXISTS (SELECT id FROM user_favoriteexpert uf WHERE uf.expert_id = uu.id and uf.user_id = {user_id}) then true
            else false
        end ) is_favorite,
        (
            SELECT json_agg(uc2.name) as categories
            FROM user_category uc2
            inner join user_userintrestorexpertise uu4 on uu4.user_id = uu.id and uu4.category_id = uc2.id
        )
        from user_user uu 
        where uu.user_type = 'expert' and uu.status = 'active'
        order by (
            select count(uc.*)
            from user_category uc 
            left join user_userintrestorexpertise uu2 on uu2.category_id = uc.id and uu2.user_id = uu.id
            left join user_userintrestorexpertise uu3 on uu3.category_id = uc.id and uu3.user_id = {user_id}
            where uu2.user_id is not null and uu3.user_id is not null
        )  desc,uu.expert_score desc  LIMIT {limit}  OFFSET {offSet};
        '''.format(
            user_id=request.user.id if request.user.is_authenticated else 0, limit=limit, offSet=offSet
        ))

        print(queryset)
        serializer = ExpertListSerializer(queryset, many=True)
        data = serializer.data
        for d in data:
            d['categories'] = d['categories'][0:2] if d['categories'] is not None else []
        return JsonResponse({
            "next_data_query": 'limit={0}&offset={1}'.format(limit, offSet + limit),
            "data": serializer.data
        })


class ExpertListSearchApi(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def get_queryset(self, request_data=None):
        queryset = User.objects.prefetch_related(
            'category').filter(user_type='expert')
        if request_data:
            # filter results for categories
            if 'filters' in request_data and request_data.get('filters'):
                if 'categories' in request_data.get('filters') and request_data.get('filters').get('categories') \
                        and type(request_data.get('filters').get('categories')) == list and request_data.get(
                    'filters').get('categories'):
                    queryset = queryset.filter(Q(category__in=request_data.get(
                        'filters').get('categories')) & Q(status='active')).distinct()
                    # for category in request_data.get('filters').get('categories'):
                    #     queryset = queryset.filter(category=category, status='active').distinct()

            searchTag = None
            if 'search' in request_data and request_data.get('search', None):
                if type(request_data.get('search')) == str:
                    searchTag = request_data.get('search')
            if 'searchBy' in request_data and request_data.get('searchBy', None):
                if type(request_data.get('searchBy')) == str:
                    searchTag = request_data.get('searchBy')

            if searchTag:
                categories = Category.objects.filter(
                    name__icontains=searchTag).values_list('id', flat=True)
                queryset = queryset.filter(Q(username__icontains=searchTag) | Q(first_name__icontains=searchTag) | Q(
                    last_name__icontains=searchTag) |
                                           Q(nick_name__icontains=searchTag) | Q(category__in=categories)).distinct()

            if 'sorting' in request_data and request_data.get('sorting'):
                if 'name' == request_data.get('sorting'):
                    queryset = queryset.filter(
                        status='active').order_by('first_name')
                if 'score' == request_data.get('sorting'):
                    queryset = queryset.filter(
                        status='active').order_by('-expert_score')

        return queryset

    # get user all info
    def post(self, request):
        try:
            limit = 20
            offSet = 0
            setLimit = request.GET.get('limit', limit)
            setOfSet = request.GET.get('offset', offSet)
            if setLimit:
                limit = int(setLimit)
            if setOfSet:
                offSet = int(setOfSet)
            queryset = self.get_queryset(request.data)[offSet:offSet + limit]
            serializer = ExpertUserSerializer(queryset, many=True)
            data = serializer.data
            for d in data:
                d['is_favorite'] = FavoriteExpert.objects.filter(user=request.user.id, expert=d['id']).count() > 0

            return JsonResponse({
                "next_data_query": 'limit={0}&offset={1}'.format(limit, offSet + limit),
                "data": data,
            })
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'data': [],
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FavoriteExpertsListApi(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    # get user afvorite ecperts info
    def get(self, request):
        queryset = User.objects.filter(id__in=FavoriteExpert.objects.filter(
            user=request.user).values_list('expert_id', flat=True))
        serializer = ExpertUserSerializer(queryset, many=True)
        data = serializer.data
        for d in data:
            d['is_favorite'] = True
        return Response(data)


class ExpertiesOrIntrestList(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    # get user all info
    def get(self, request):
        serializer = self.get_serializer(
            request.user.category,
            many=True
        )
        return Response(serializer.data)


class ExpertDetails(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = User.objects.filter(user_type='expert')
    serializer_class = UserListSerializer

    # get expert details
    def get(self, request, *args, **kwargs):
        serializer = UserListSerializer(self.get_object(), many=False)
        return Response(serializer.data)


class AddFavoriteExpert(generics.CreateAPIView):
    serializer_class = FavoriteExpertSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            request.data['user'] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RemoveFavoriteExpert(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            favoriteExperts = FavoriteExpert.objects.filter(
                user=request.user.id, expert=request.data.get('expert'))
            if favoriteExperts.exists():
                favoriteExperts.delete()
            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryListApi(generics.ListAPIView):
    permission_classes = (AllowAny,)

    # get user all info
    def get(self, request):
        queryset = CategoryList.objects.raw('''
        select uc.*,
        ( case
            when EXISTS (SELECT id FROM user_userintrestorexpertise uui WHERE uui.category_id = uc.id and uui.user_id = {user_id}) then true
            else false
        end ) is_selected
        from user_category uc;
        '''.format(
            user_id=request.user.id if request.user.is_authenticated else 0
        ))
        serializer = CategoryListSerializer(queryset, many=True)
        return Response(serializer.data)


class AddIntrestOrExpertise(generics.CreateAPIView):
    serializer_class = UserIntrestOrExpertiseSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            request.data['user'] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RemoveIntrestOrExpertise(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            favoriteExperts = UserIntrestOrExpertise.objects.filter(
                user=request.user.id, category=request.data.get('category'))
            if favoriteExperts.exists():
                favoriteExperts.delete()
            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetPaymentOrderRequest(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            # get mandatory field value program id from path params
            batch_id = kwargs.get("batch_id")
            if not request.user.is_authenticated:
                user_id = request.data["user_id"]
                request.user = User.objects.get(id=int(user_id))

            # fetch program data if exist
            if ProgramBatch.objects.filter(id=batch_id).exists():
                programBatch = ProgramBatch.objects.get(id=batch_id)
                program = programBatch.program
            else:
                return JsonResponse({
                    'message': 'No Data Exist for Requested Program'
                },
                    safe=False,
                    status=status.HTTP_400_BAD_REQUEST
                )
            discount = 0
            discount_code = request.data.get('discount_code', None)
            print("discount_code: ", discount_code)

            discount_from_db = None
            if discount_code is not None:
                if discount_code and not discount_code.isspace():
                    discount_from_db = Discount.objects.get(code=discount_code)

            if discount_from_db is not None:
                discount = float(discount_from_db.discount)

            user_payble_amount_in_inr = float(
                programBatch.offer_price if programBatch.offer_price else programBatch.price) - discount

            user_payble_amount = user_payble_amount_in_inr * 100  # it is in paisa

            # make notes object
            notes_params_count = 0  # notes_data should have limit of 15 params
            notes_data = {
                'account_user_name': request.user.username,
                'account_holder_name': request.user.first_name,
                'account_holder_mobile': request.user.mobile if request.user.mobile else "",
                'account_holder_email': request.user.email if request.user.email else "",
            }
            notes_params_count += 4
            if request.data:
                for key, value in request.data.items():
                    if key and value:
                        key = str(key)
                        value = str(value)
                        if notes_params_count < 16 and len(key + value) < 256:
                            notes_data[key] = value
                            notes_params_count += 1

            # start transaction
            userOrder = UserOrder.objects.create(
                user=request.user,
                programBatch=programBatch,
                amount=user_payble_amount,
            )

            # create order request and save in database
            order_request = {
                "amount": str(int(user_payble_amount)),
                "currency": "INR",
                "receipt": userOrder.getRecieptId(),
                'notes': notes_data
            }
            userOrder.order_request = order_request
            userOrder.save()

            # genrate and get order id
            order_data = razorpay_client.order.create(data=order_request)
            userOrder.order_id = order_data.get('id')
            userOrder.order_response_before_payment = order_data
            userOrder.save()

            # make payment request
            payment_request = {
                'key': env_constants.getRazorpayKey(),
                'amount': str(int(user_payble_amount)),
                'name': program.title,
                # Generate order_id using Orders API
                'order_id': order_data.get('id'),
                'description': 'Yellow Squash Program : ' + program.title,
                'timeout': 300,  # in seconds
                'prefill': {
                    'contact': request.user.mobile,
                    'email': request.user.email
                },
                'notes': notes_data
            }

            # update payment request in database
            userOrder.payment_request = payment_request
            userOrder.save()

            return JsonResponse(
                data={
                    'message': 'success',
                    'order_id': order_data.get('id'),
                    'request': payment_request
                },
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            logger.exception(
                "error while genrating payment request : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PostPaymentOrderResponse(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            error_message = ''
            userOrder = None

            if (not request.user.is_authenticated):
                request.user = User.objects.get(
                    id=int(request.data.get("user_id")))

            # validare request and fetch payment data from api
            if 'order_id' in request.data and UserOrder.objects.filter(order_id=request.data.get('order_id')).exists():
                userOrder = UserOrder.objects.filter(
                    order_id=request.data.get('order_id')).first()
                # save order data even if request failed
                order_data = razorpay_client.order.fetch(
                    request.data.get('order_id'))
                userOrder.order_response_after_payment = order_data
                userOrder.save()

                # fetch payment data from order even for failed payments if exist
                payment_id = None
                order_payments_data = razorpay_client.order.payments(
                    request.data.get('order_id'))
                if order_payments_data:
                    for payment in order_payments_data.get('items'):
                        if payment and 'id' in payment and payment.get('id'):
                            userOrder.payment_id = payment.get('id')
                            userOrder.payment_response_on_fetch = payment
                            userOrder.save()

                            # if got one success payment response then no need to process
                            if 'status' in payment and payment.get('status') and payment.get('captured'):
                                break

                if 'payment_response' in request.data:
                    # save payment response
                    userOrder.payment_response_from_ui = request.data.get(
                        'payment_response')
                    userOrder.save()

                    if 'paymentId' in request.data.get('payment_response') and 'orderId' in request.data.get(
                            'payment_response') and 'signature' in request.data.get('payment_response'):
                        # verify payment before giving confirmation to user
                        razorpay_client.utility.verify_payment_signature({
                            'razorpay_order_id': request.data.get('payment_response').get('orderId'),
                            'razorpay_payment_id': request.data.get('payment_response').get('paymentId'),
                            'razorpay_signature': request.data.get('payment_response').get('signature'),
                        })

                        # save payment data as we have payment id now
                        payment_id = request.data.get(
                            'payment_response').get('paymentId')
                        payment_data = razorpay_client.payment.fetch(
                            payment_id)
                        userOrder.payment_id = payment_id
                        userOrder.payment_response_on_fetch = payment_data
                        userOrder.save()

                    else:
                        error_message = 'No payment response Data found. Amount will be refunded if already deducted.'
                else:
                    error_message = 'No payment response Data found. Amount will be refunded if already deducted.'
            else:
                error_message = 'Order Not Found due to incorrect order id. Amount will be refunded if already deducted.'

            # if system getting error in fetching data then give it in response without any further process
            if error_message:
                if userOrder:
                    userOrder.payment_status = 'failed'
                    userOrder.save()

                return JsonResponse({
                    'message': error_message
                },
                    safe=False,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # validate order and payment data from razor pay and from our system
            # order id should be same in paymeny and order resposne
            if payment_data.get('order_id') != order_data.get('id'):
                error_message = "spam response : order and payment data doesn't match"

            # if system getting error while validating data then give it in response without any further process
            if error_message:
                if userOrder:
                    userOrder.payment_status = 'failed'
                    userOrder.save()

                return JsonResponse({
                    'message': error_message
                },
                    safe=False,
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                userOrder.payment_status = 'completed'
                userOrder.save()

            # add user to program
            serializer = ProgramBatchUserSerializer(data={
                'programBatch': userOrder.programBatch.id,
                'user': request.user.id,
                'status': "active"
            })
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return JsonResponse(
                data={
                    'message': 'success',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            logger.exception(
                "error while payment response parsing : ", exc_info=err)

            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddUserDeviceToken(generics.CreateAPIView):
    serializer_class = UserDeviceTokenSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            if 'token' in request.data and not UserDeviceToken.objects.filter(
                    device_token=request.data.get('token')).exists():
                serializer = self.get_serializer(data={
                    'user': request.user.id,
                    'device_token': request.data.get('token'),
                    'device': request.data.get('device')
                })
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            else:
                userDeviceToken = UserDeviceToken.objects.get(
                    device_token=request.data.get('token'))
                userDeviceToken.user = request.user
                userDeviceToken.save()
                serializer = self.get_serializer(userDeviceToken, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExpertTotalCount(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        total_count = User.objects.filter(
            user_type='expert', status="active").count()
        return JsonResponse({
            "total_expert": total_count
        }, status=status.HTTP_200_OK)


class LocationList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        locations = Location.objects.all()
        locations_serializer = LocationSerializer(locations, many=True)
        return Response(locations_serializer.data, status=status.HTTP_200_OK)


class LanguageList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        languages = Languages.objects.all()
        languages_serializer = LanguageSerializer(languages, many=True)
        return Response(languages_serializer.data, status=status.HTTP_200_OK)


class TimezoneList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        timezones = TimeZone.objects.all()
        timezones_serializer = TimezoneSerializer(timezones, many=True)
        return Response(timezones_serializer.data, status=status.HTTP_200_OK)


class ExpertiseList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        expertises = Expertise.objects.all()
        expertises_serializer = ExpertiseSerializer(expertises, many=True)
        return Response(expertises_serializer.data, status=status.HTTP_200_OK)


class RoleList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        role = Role.objects.all()
        role_serializer = RoleSerializer(role, many=True)
        return Response(role_serializer.data, status=status.HTTP_200_OK)


class ExpertTeamMembers(views.APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        # Get User
        user = request.user
        try:
            is_member_exists = ExpertTeamMember.objects.filter(user=user, is_active=True)
            expert_det = {}
            expert_det['team_member_id'] = user.id
            expert_det['role'] = 'Program Expert'
            expert_det['name'] = user.first_name
            expert_det['phone'] = user.mobile
            expert_det['email'] = user.email
            if is_member_exists:
                expert_det['is_active'] = False
            else:
                expert_det['is_active'] = True
            expert_det['is_expert'] = True

            # Create Expert Team Member Instance
            member = ExpertTeamMember.objects.filter(user=user)
            # Pass instance and get data
            member_serializer = ExpertTemMemberSerializer(member, many=True)
            data = member_serializer.data
            data.append(expert_det)
            return Response(data, status=status.HTTP_200_OK)
        except ExpertTeamMember.DoesNotExist as e:
            return Response({"message": "Team member does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        # Upto 5 members can add more than that not allowed
        if ExpertTeamMember.objects.filter(user=user).count() <= 4:

            # Create Expert Team Member Instance
            member = ExpertTeamMember(user=user)
            sendOtp = Otp()

            randomGeneratedPassword = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(12))

            if User.objects.filter(email=request.data.get('email')).exists():
                return Response({"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(mobile=request.data.get('phone')).exists():
                return Response({"message": "Mobile already exists"}, status=status.HTTP_400_BAD_REQUEST)

            member.role = Role.objects.get(role_id=request.data.get('role'))

            # Create searializer andpass data
            member_serializer = ExpertTemMemberSerializer(member, data=request.data)
            # Check validation
            if member_serializer.is_valid():
                # Save data if data validation is correct
                member_serializer.save()

                user = User.objects.create(username=request.data.get('email'), mobile=request.data.get('phone'),
                                           email=request.data.get('email'), user_type="teammember")
                user.set_password(randomGeneratedPassword)
                user.save()

                # sending sendinblue email
                task = {
                    "sender": {
                        "name": "YellowSquash",
                        "email": "yellowsquash@gmail.com"
                    },
                    "to": [
                        {
                            "email": "{0}".format(user.email),
                            "name": "{0}".format(user.first_name)
                        }
                    ],
                    "templateId": 73,
                    "params": {"otp": "test"}
                }

                data = sendOtp.EmailOtp(task)
                print(data)

                # Response User with 201 Code
                return Response(member_serializer.data, status=status.HTTP_201_CREATED)

            # If Validation Not accepted
            else:
                # Send Error Response
                return Response(member_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You have exceeded your limit"}, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = request.user
        try:
            member = ExpertTeamMember.objects.get(team_member_id=id)
            member.role = Role.objects.get(role_id=request.data.get('role'))
            request.data._mutable = True
            request.data['is_active'] = member.is_active
            request.data._mutable = False

            # Create searializer and pass data
            member_serializer = ExpertTemMemberSerializer(member, data=request.data)
            # Check validation
            if member_serializer.is_valid():
                # Save data if data validation is correct
                member_serializer.save()
                # Response User with 201 Code
                return Response(member_serializer.data, status=status.HTTP_201_CREATED)
            # If Validation Not accepted
            else:
                # Send Error Response
                return Response(member_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ExpertTeamMember.DoesNotExist as e:
            return Response({"message": "Expert Team Member does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            member = ExpertTeamMember.objects.get(team_member_id=id)
            user = User.objects.filter(mobile=member.phone,
                                       email=member.email, user_type="teammember").delete()
            member.delete()
            success_msg = {"message": "Team member deleted successfully"}
            return Response(success_msg, status=status.HTTP_200_OK)
        except ExpertTeamMember.DoesNotExist as e:
            return Response({"message": "Team member does not exist"}, status=status.HTTP_404_NOT_FOUND)


class AllCategoryList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        category = Category.objects.all()
        category_serializer = CategorySerializer(category, many=True)
        return Response(category_serializer.data, status=status.HTTP_200_OK)


class DegreeCertificationList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        degree = DegreeCertification.objects.all()
        degree_serializer = DegreeCertificationSerializer(degree, many=True)
        return Response(degree_serializer.data, status=status.HTTP_200_OK)


class ChangeExpertTeamMemberStatus(views.APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id):
        try:
            # 0 -team member 1-expert
            # Check if user is team member or expert and update active status accordingly
            is_expert = int(request.data.get('is_expert', 0))
            if is_expert == 0:
                member = ExpertTeamMember.objects.get(team_member_id=id)
                member.is_active = True
                member.save()
                data = ExpertTemMemberSerializer(member).data
            else:
                ExpertTeamMember.objects.filter(user=request.user).update(is_active=False)
                data = {}
            #  Update other team member status to false
            ExpertTeamMember.objects.filter(user=request.user).exclude(team_member_id=id).update(is_active=False)
            return Response(data, status=status.HTTP_200_OK)
        except ExpertTeamMember.DoesNotExist as e:
            return Response({"message:Team member does not exist"}, status=status.HTTP_404_NOT_FOUNDt)


class ExpertCategoryWiseList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'professional_title']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        queryset = User.objects.filter(user_type="expert", status='active')

        if category:
            category = [int(c) for c in category.split(',')]
            queryset = queryset.filter(user_type="expert", category__in=category, status='active')

        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        expert_serializer = ExpertSerializer(queryset, many=True, context={'user': request.user})
        data = expert_serializer.data
        # return Response(data,status=status.HTTP_200_OK)
        result = self.get_paginated_response(data[start_limit:end_limit]).data
        return Response(success_response(result), status=status.HTTP_200_OK)


class AllCategory(views.APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        category = Category.objects.all().values('id', 'name')
        return Response(success_response(category), status=status.HTTP_200_OK)


class FavouriteExpertAPI(views.APIView):

    def post(self, request, expert_id):
        user = request.user
        try:
            if User.objects.filter(id=expert_id).exists():
                if FavoriteExpert.objects.filter(user=user, expert_id=expert_id).exists():
                    return Response(success_response("Expert already added to favourite"), status=status.HTTP_200_OK)
                else:
                    favourite = FavoriteExpert.objects.create(user=user, expert_id=expert_id)
                    favourite.save()
                    return Response(success_response("Expert added to favourite"), status=status.HTTP_201_CREATED)
            else:
                return Response(error_response("Expert not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, expert_id):
        user = request.user
        try:
            if User.objects.filter(id=expert_id).exists():
                favourite = FavoriteExpert.objects.filter(user=user, expert_id=expert_id)
                favourite.delete()
                return Response(success_response("Expert removed from favourite"), status=status.HTTP_200_OK)
            else:
                return Response(error_response("Expert not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpertFavouriteList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(id__in=FavoriteExpert.objects.filter(
            user=user).values_list('expert_id', flat=True))
        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = ExpertSerializer(queryset, many=True, context={'user': request.user})
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)


class ExpertDetail(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, expert_id):
        try:
            queryset = User.objects.get(id=expert_id)
            serializer = ExpertDetailSerializer(queryset, many=False)
            return Response(success_response(serializer.data), status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(error_response("Expert not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(error_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
