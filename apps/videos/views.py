import json
import traceback

from django.shortcuts import render
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination

from .models import *
from .serializer import *

from ..common_utils.MobileOtp import Otp
from ..notify import service as notifyService
from ..user.models import UserDeviceToken
from apps.common_utils.standard_response import success_response, error_response
from apps.healthpedia.serializers import VideoListSerializer

class TagList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    queryset = Tag.objects.filter(status='active')


class CreateVideo(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self, expert_id=None):
        if expert_id:
            queryset = Video.objects.filter(expert_id=expert_id).order_by('-updated_at')
        else:
            queryset = Video.objects.all().order_by('-updated_at')

        return queryset

    def get(self, request):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        if request.user.user_type == "admin":
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset(request.user.id)

        page = self.paginate_queryset(queryset)
        video_serializer = VideoSerializer(queryset, many=True)
        return self.get_paginated_response(video_serializer.data[start_limit:end_limit])
        # return Response(video_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        sendOtp = Otp()
        try:
            if Video.objects.filter(title=request.data.get('title')).exists():
                return Response({
                    "message": "Video with title {0} already exists.Please try again with some other name.".format(
                        request.data.get('title'))})

            thumbnail = request.data['thumbnail']
            upload_video = request.data['upload_video']
            print(request.data)
            if thumbnail:
                # validate file extension
                image_name = thumbnail.name.split(".")[-1]
                format = ['jpg', 'jpeg', 'png']

                if image_name not in format:
                    return Response({"message": "Invalid image format.Allowed only jpg,jpeg and png"})

            video = Video.objects.create(expert=request.user, title=request.data.get('title'),
                                         thumbnail=thumbnail, upload_video=upload_video,
                                         status=request.data.get('status'))

            if 'tags' in request.data:
                tags = []
                tag_data = json.loads(request.data.get('tags'))
                for tag in tag_data:
                    tagObj, created = Tag.objects.get_or_create(tag_name=tag)
                    tags.append(tagObj.id)
                video.tags.add(*tags)

            if "category" in request.data:
                category_list = json.loads(request.data.get('category'))
                video.category.add(*category_list)

            video.save()

            # sending email
            templateId = None
            if request.data['status'] == "requested":
                templateId = 30
            task = {
                "sender": {
                    "name": "YellowSquash",
                    "email": "yellowsquash@gmail.com"
                },
                "to": [
                    {
                        "email": "info@yellowsquash.in",
                        "name": "yellowsquash"
                    }
                ],
                "templateId": templateId,
                "params": {'slug': "{0}".format(video.slug)}
            }
            sendOtp.EmailOtp(task)

            # notify all admins about the new blog create
            notifyService.notifyMobileAppUser(
                title="{user_name} requested new video : {title}".format(user_name=request.user.first_name,
                                                                         title=video.title),
                body=video.title,
                device_tokens=list(
                    UserDeviceToken.objects.filter(user__user_type='admin').values_list('device_token', flat=True)),
                payload={},
                small_img_url=None,
                large_img_url=None
            )

            return Response({'message': 'Video added successfully'}, status=status.HTTP_200_OK)
        except BaseException as e:
            traceback.print_exc()
            return Response({
                'message': 'Something went wrong',
            },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, expert=request.user.id)
            video.title = request.data.get('title')
            video.status = request.data.get('status')

            thumbnail = request.data['thumbnail']
            print(f"{thumbnail=}")
            if thumbnail:
                # validate file extension
                image_name = thumbnail.name.split(".")[-1]
                format = ['jpg', 'jpeg', 'png']

                if image_name not in format:
                    return Response({"message": "Invalid image format.Allowed only jpg,jpeg and png"})

            video.thumbnail = thumbnail
            video.upload_video = request.data['upload_video']

            if 'tags' in request.data:
                video.tags.remove(*video.tags.all())
                tags = []
                tag_data = json.loads(request.data.get('tags'))
                for tag in tag_data:
                    tagObj, created = Tag.objects.get_or_create(tag_name=tag)
                    tags.append(tagObj.id)
                video.tags.add(*tags)

            if "category" in request.data:
                video.category.remove(*video.category.all())
                category_list = json.loads(request.data.get('category'))
                video.category.add(*category_list)

            video.save()
            video_serializer = VideoSerializer(video)
            return Response({"message": "Video updated successfully", "data": video_serializer.data},
                            status=status.HTTP_200_OK)
        except Video.DoesNotExist as e:
            return Response({"message": "Video does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, expert=request.user)
            video.delete()
            return Response({"message": "Video deleted successfully"}, status=status.HTTP_200_OK)
        except Video.DoesNotExist as e:
            raise NotFound(detail="Video Does not exist")


class VideoStatusUpdate(generics.UpdateAPIView):
    def put(self, request):
        sendOtp = Otp()
        video_id = request.data['video_id']
        video_status = request.data['video_status']
        try:
            if request.user.user_type == "admin":
                video = Video.objects.get(id=video_id)
                if video_status == "approved" or video_status == "published":
                    # send notification to expert about his video status
                    if UserDeviceToken.objects.filter(user=video.expert).exists():
                        templateId = 31
                        task = {
                            "sender": {
                                "name": "YellowSquash",
                                "email": "yellowsquash@gmail.com"
                            },
                            "to": [
                                {
                                    "email": "{0}".format(video.expert.email),
                                    "name": "{0}".format(video.expert.first_name)
                                }
                            ],
                            "templateId": templateId,
                            "params": {"fullname": "{0}".format(video.expert.first_name),
                                       'article_name': "{0}".format(video.title), 'slug': "{0}".format(video.slug)}
                        }
                        sendOtp.EmailOtp(task)
                        notifyService.notifyMobileAppUser(
                            title="Your video : {article} got {status}".format(article=video.title,
                                                                               status=video_status),
                            body=video.title,
                            device_tokens=list(
                                UserDeviceToken.objects.filter(user=video.expert).values_list('device_token',
                                                                                              flat=True)),
                            payload={},
                            small_img_url=None,
                            large_img_url=None
                        )

            elif request.user.user_type == "expert":
                if Video.objects.get(id=video_id).exclude(status__in=['approved', 'published']):
                    if video_status == "approved" or video_status == "published":
                        message = "Expert can't approve/publish non approved video"
                        return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                message = "This user is not authorized to upadte video status !"
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

            video.status = video_status
            video.save()
            return Response({"message:Video status updated successfully"}, status=status.HTTP_200_OK)

        except Video.DoesNotExist as e:
            return NotFound(detail="Video does not exist")
        except BaseException as be:
            return Response({"message:Something went wrong"})


class FavouriteVideo(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, video_id):
        try:
            user = request.user
            if Video.objects.filter(id=video_id, favourite=user).exists():
                return Response(success_response("Video already added to favourite"), status=status.HTTP_200_OK)
            else:
                video = Video.objects.get(id=video_id)
                video.favourite.add(user)
                video.save()

                return Response(success_response("Video added to favourite"), status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response(error_response("Video does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, video_id):
        try:
            user = request.user
            video = Video.objects.get(id=video_id)
            video.favourite.remove(user)
            video.save()

            return Response(success_response("Video removed from favourite"), status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response(error_response("Video does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavouriteVideoList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Video.objects.filter(favourite__in=[user]).order_by('created_at')
        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = VideoListSerializer(queryset, many=True)
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)