import json

from django.shortcuts import render
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from .models import *
from .serializer import *
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import views, filters
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import LimitOffsetPagination

from datetime import datetime
import pytz, base64
from icalendar import vCalAddress, vText, Calendar, Event
from datetime import datetime
from django.db.models import Q

from apps.common_utils.SendEmailBlueBirdAPI import SendEmailBlueBirdAPI
from apps.user.models import User, Category
from apps.blog.models import Blog

# Create your views here.
from ..common_utils.standard_response import success_response,error_response


class WebinarList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            # display_all = request.GET.get('display_all')
            # print(display_all)
            # if display_all is None:
            #     queryset = Webinar.objects.all().order_by('displayOrder')[:10]
            # else:
            #     queryset = Webinar.objects.all().order_by('displayOrder')

            currentDate = datetime.today().strftime('%Y-%m-%d')
            # getting all the webinar which are active and webinar date less than current date

            queryset = Webinar.objects.filter(Q(status='Active') and Q(webinar_date__lt=currentDate))

            if (queryset):
                for qs_obj in queryset:
                    qs_obj.status = 'Inactive'
                    qs_obj.save()

            queryset = Webinar.objects.filter(status='Active').order_by('displayOrder')

            print(request.GET)

            serializer = WebinarSerializer(queryset, many=True)

            return JsonResponse(serializer.data, safe=False)
        except BaseException as err:
            # logger.exception("Error Occured While getting webinar : ", exc_info=err)
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):

        try:
            category = None
            searchTag = None
            currentDate = datetime.today().strftime('%Y-%m-%d')
            limit = int(request.GET.get('limit', 3))
            offSet = int(request.GET.get('offset', 0))
            if (request.data.get('filters', None) and request.data.get('filters').get('categories', None)):
                category = request.data.get('filters').get('categories', None)
            if 'search' in request.data and request.data.get('search', None):
                if type(request.data.get('search')) == str:
                    searchTag = request.data.get('search')
            queryset = Webinar.objects.filter(Q(status='Active') and Q(webinar_date__lt=currentDate))

            if (queryset):
                for qs_obj in queryset:
                    qs_obj.status = 'Inactive'
                    qs_obj.save()

            queryset = Webinar.objects.filter(status='Active').order_by('displayOrder')
            if category:
                queryset = queryset.filter(category__in=category).distinct()
            if searchTag:
                categories = Category.objects.filter(name__icontains=searchTag).values_list('id', flat=True)
                queryset = queryset.filter(Q(title__icontains=searchTag) | Q(category__in=categories)).distinct()

            queryset = queryset[offSet:limit + offSet]
            webinarSerializerData = WebinarSerializer(queryset, many=True).data

            return JsonResponse({
                "next_data_query": 'limit={limit}&offset={offset}'.format(
                    limit=limit,
                    offset=offSet + limit
                ),
                "data": webinarSerializerData
            })

        except Exception as err:
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WebinarDetails(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Webinar.objects.all()
    serializer_class = WebinarDetailSerializer


class WebinarDetailsBySlug(views.APIView):

    def get_details_by_slug(request, slug):
        webinar = Webinar.objects.get(slug=slug)
        serializer = WebinarDetailSerializer(webinar, many=False)
        print(serializer.data)
        expert_id = serializer.data["expert"]["id"]
        user_img = User.objects.get(id=expert_id).user_img
        serializer.data["expert"]["user_img"] = user_img
        return JsonResponse(serializer.data, safe=False)

    def get_details_by_id(request, id):
        webinar = Webinar.objects.get(id=id)
        serializer = WebinarDetailSerializer(webinar, many=False)
        return JsonResponse(serializer.data, safe=False)


class WebinarSubscribe(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    # get all info
    def post(self, request):
        try:
            webinar = Webinar.objects.get(id=request.data['webinarId'])
            print(request.data)
            user = None
            name = request.data['name']
            email = request.data['email']
            whatsapp_mobile_no = request.data['whatsapp_mobile_no']
            if request.user.is_authenticated:
                user = request.user
            webinarSubscriberData = WebinarSubscriber.objects.create(name=name, email=email,
                                                                     whatsapp_mobile_no=whatsapp_mobile_no, user=user,
                                                                     webinar=webinar)

            if webinar.blue_bird_email_template_id is None:
                print('webinar has no email template, email invite will not be sent to user')
            else:
                mail_meta_data = {
                    "sender": {"name": "YellowSquash", "email": "yellowsquash@gmail.com"},
                    "to": [{"email": email, "name": name}],
                    "templateId": int(webinar.blue_bird_email_template_id),
                    "attachment": [
                        {
                            "content": self.__get_base64_ics_string(webinar, name, email),
                            "name": webinar.slug + '.ics'
                        }
                    ],
                    "params": {
                        "name": name,
                        "program_name": webinar.title,
                        "program_date": str(webinar.webinar_date)
                    }
                }
                ack = SendEmailBlueBirdAPI.send_mail(mail_meta_data)
                print(ack)

            return JsonResponse(
                data={"message": "done"},
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as ie:
            print(ie)
            return JsonResponse(
                {'message': 'You already subscribed for this webinar', 'error': str(ie), 'type': 'warning'}, safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except BaseException as err:
            print(err)
            return JsonResponse({'message': 'Unable to subscribe', 'error': str(err), 'type': 'error'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __get_base64_ics_string(self, webinar, subscriber_name, subscriber_email):
        cal = Calendar()

        event = Event()
        event.add('summary', webinar.title)
        event.add('dtstart', datetime(webinar.webinar_date.year, webinar.webinar_date.month, webinar.webinar_date.day,
                                      webinar.start_time.hour, webinar.start_time.minute, 0,
                                      tzinfo=pytz.timezone('Asia/Kolkata')))
        event.add('dtend', datetime(webinar.webinar_date.year, webinar.webinar_date.month, webinar.webinar_date.day,
                                    webinar.end_time.hour, webinar.end_time.minute, 0,
                                    tzinfo=pytz.timezone('Asia/Kolkata')))
        event.add('dtstamp', datetime(webinar.webinar_date.year, webinar.webinar_date.month, webinar.webinar_date.day,
                                      webinar.end_time.hour, webinar.end_time.minute, 0,
                                      tzinfo=pytz.timezone('Asia/Kolkata')))

        organizer = vCalAddress('MAILTO:yellowsquash@gmail.com')
        organizer.params['cn'] = vText('YellowSquash')
        organizer.params['role'] = vText('CHAIR')
        event['organizer'] = organizer
        event['location'] = vText('New Delhi, India')

        event['uid'] = webinar.slug + '@yellowsquash.in'
        event.add('priority', 5)

        attendee = vCalAddress('MAILTO:' + subscriber_email)
        attendee.params['cn'] = vText(subscriber_name)
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
        event.add('attendee', attendee, encode=0)

        cal.add_component(event)

        return base64.b64encode(cal.to_ical()).decode('utf-8')


class WebinarCategoryWiseList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'subtitle']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get categories param if exists
        # categories = json.loads(self.request.data.get('categories', '[]'))
        categories = json.loads(self.request.query_params.get('categories', '[]'))
        print(f"{categories=}")
        if categories:
            webinar = Webinar.objects.filter(category__in=categories, status='Active')
        else:
            webinar = Webinar.objects.filter(status='Active')

        return webinar

    def get(self, request):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        webinar_serializer = WebinarCategoryWiseSerializer(queryset, many=True)
        data = webinar_serializer.data

        # return Response(data,status=status.HTTP_200_OK)
        return self.get_paginated_response(data[start_limit:end_limit])


class UpcomingWebinar(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get(self, request):
        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 3))
        end_limit = start_limit + limit

        today = datetime.today().strftime('%Y-%m-%d')
        webinar = Webinar.objects.filter(status='Active', webinar_date__gt=today)
        page = self.paginate_queryset(webinar)
        webinar_serializer = UpcomingWebinarSerializer(webinar, many=True)
        data = webinar_serializer.data
        # return Response(data,status=status.HTTP_200_OK)
        return self.get_paginated_response(data[start_limit:end_limit])


class GetWebinarDetails(views.APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id):
        try:
            webinar = Webinar.objects.get(id=id)
            webinar_serializer = GetWebinarDetailSerializer(webinar,many=False)
            return Response(success_response(webinar_serializer.data), status=status.HTTP_200_OK)
        except Webinar.DoesNotExist:
            return Response(error_response("Webinar doesn't exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            print(err)
            return Response(error_response(str(err)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavouriteWebinar(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self,request,webinar_id):
        try:
            user = request.user
            if Webinar.objects.filter(id=webinar_id,favourite=user).exists():
                return Response(success_response("Webinar already added to favourite"),status=status.HTTP_200_OK)
            else:
                webinar = Webinar.objects.get(id=webinar_id)
                webinar.favourite.add(user)
                webinar.save()

                return Response(success_response("Webinar added to favourite"),status=status.HTTP_200_OK)
        except Webinar.DoesNotExist:
            return Response(error_response("Webinar does not exist"),status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response(error_response(str(err)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, webinar_id):
        try:
            user = request.user
            webinar = Webinar.objects.get(id=webinar_id)
            webinar.favourite.remove(user)
            webinar.save()

            return Response(success_response("Webinar removed from favourite"), status=status.HTTP_200_OK)
        except Webinar.DoesNotExist:
            return Response(error_response("Webinar does not exist"), status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavouriteWebinarList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Webinar.objects.filter(favourite__in=[user]).order_by('createdAt')
        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = WebinarListSerializer(queryset, many=True, context={'user': request.user})
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)


class WebinarListingAPI(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        queryset = Webinar.objects.filter(status='Active').order_by('-createdAt')

        if category:
            category = [int(c) for c in category.split(',')]
            queryset = queryset.filter(category__in=category).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = WebinarListSerializer(queryset, many=True, context={'user': request.user})
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)

