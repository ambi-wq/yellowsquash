import json
import requests
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, mixins, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import serializer_helpers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination

from .models import Blog, Tag, BlogView, BlogComment, BlogLike, BlogShare, BlogStates
from .serializers import *
from apps.user.models import User, Category, UserDeviceToken
from apps.notify import service as notifyService

from apps.common_utils.Aws import Aws, AwsFilePath
from apps.common_utils.MobileOtp import Otp
import logging
import re
from django.db.models import Count
from apps.common_utils.standard_response import success_response, error_response
from apps.healthpedia.serializers import BlogListSerializer as FavouriteBlogListSerializer

logger = logging.getLogger(__name__)


class TagsList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagsSerializer

    def get(self, request, *args, **kwargs):
        queryset = Tag.objects.filter(status='active')
        serializer = self.serializer_class(queryset, many=True)
        return JsonResponse(data=success_response(serializer.data), status=status.HTTP_200_OK)


class SearchBlogList(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def get_queryset(self, request_data=None):
        queryset = Blog.objects.prefetch_related('expert', 'blog_state').filter(status='published').order_by(
            '-updated_at')
        if request_data:
            if 'filters' in request_data and request_data.get('filters'):
                if 'categories' in request_data.get('filters') and request_data.get('filters').get('categories') \
                        and type(request_data.get('filters').get('categories')) == list and request_data.get(
                    'filters').get('categories'):
                    # for category in request_data.get('filters').get('categories'):
                    #     queryset = queryset.filter(categories=category).distinct()

                    queryset = queryset.filter(categories__in=request_data.get('filters').get('categories')).distinct()

                if 'tags' in request_data.get('filters') and request_data.get('filters').get('tags') \
                        and type(request_data.get('filters').get('tags')) == list and request_data.get('filters').get(
                    'tags'):
                    queryset = queryset.filter(tags__in=request_data.get('filters').get('tags'))
                if 'related_categories' in request_data.get('filters') and request_data.get('filters').get(
                        'related_categories') \
                        and type(request_data.get('filters').get('related_categories')) == list or request_data.get(
                    'filters').get('related_categories'):
                    queryset = queryset.filter(
                        categories__in=request_data.get('filters').get('related_categories')).distinct()
                    queryset = queryset.exclude(slug=request_data.get('filters').get('slug'))

            # sorting based on likes
            if 'sorting' in request_data:
                if "like" in request_data.get('sorting'):
                    queryset = queryset.annotate(
                        blog_like_count=Count('blog_state', filter=Q(blogstates__is_like=True))).order_by(
                        '-blog_like_count')

            if 'search' in request_data and request_data.get('search', None):
                if type(request_data.get('search')) == str:
                    searchTag = request_data.get('search')
                    tags = Tag.objects.filter(tag_name__icontains=searchTag).values_list('id', flat=True)
                    categories = Category.objects.filter(name__icontains=searchTag).values_list('id', flat=True)
                    queryset = queryset.filter(
                        Q(title__icontains=searchTag) | Q(summary__icontains=searchTag) | Q(slug__icontains=searchTag) |
                        Q(tags__in=tags) | Q(categories__in=categories)).distinct()

        return queryset

    # get all info
    def post(self, request):
        # if not requested with limti and ofset use default as :
        # limit : 20
        # ofset : 0
        limit = int(request.GET.get('limit', 20))
        offSet = int(request.GET.get('offset', 0))
        queryset = self.get_queryset(request.data)[offSet: (offSet + limit)]
        serializer = BlogListSerializer(queryset, many=True)
        return JsonResponse({
            "next_data_query": 'limit={limit}&offset={offset}'.format(
                limit=limit,
                offset=offSet + limit
            ),
            "data": serializer.data,
        })


class ExpertBlogList(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get_queryset(self, expert_id=None):
        queryset = Blog.objects.filter(status='approved', expert_id=expert_id).order_by('-updated_at')
        return queryset

    # get all info
    def get(self, request, expert_id):
        queryset = self.get_queryset(expert_id)
        serializer = BlogListSerializer(queryset, many=True)
        return Response(serializer.data)


class MyBlogList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self, expert_id=None):
        if expert_id:
            queryset = Blog.objects.filter(expert_id=expert_id).prefetch_related('categories', 'expert',
                                                                                 'bloglike_set').order_by('-updated_at')
        else:
            queryset = Blog.objects.prefetch_related('categories', 'expert', 'bloglike_set').order_by('-updated_at')
        return queryset

    # get all info
    def get(self, request):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        if request.user.user_type == 'admin':
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset(request.user.id)
        page = self.paginate_queryset(queryset)
        serializer = BlogListSerializer(queryset, many=True)
        response = self.get_paginated_response(serializer.data[start_limit:end_limit])
        return JsonResponse(success_response(response.data), status=status.HTTP_200_OK)


class BlogDetails(generics.ListAPIView):
    permission_classes = (AllowAny,)

    # get all info
    def get(self, request, slug):
        try:
            queryset = Blog.objects.get(slug=slug)
            serializer = BlogDetailSerializer(queryset, many=False)
            return Response(success_response(serializer.data), status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return JsonResponse(error_response('Blog does not exist'), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            print(err)
            return JsonResponse(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogViewCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug):
        blog_obj = Blog.objects.get(slug=slug)
        BlogView.objects.create(
            user=request.user,
            blog_id=blog_obj.id,
        )

        nestr = re.sub(r'[^a-zA-Z0-9]', r'', slug)
        blog_view_count = blog_obj.blogview_set.count()
        print("blog view count:", blog_view_count)
        notifyService.centrifugePublish(
            channel=nestr,
            data={
                "command": 'view',
                "user_id": request.user.id,
                "blog": blog_obj.id,
                "view_count": blog_view_count,
                "user": request.user.get_user_fullname(),
            }
        )

        return Response(status=201)


class BlogCommentsApi(generics.ListAPIView):
    permission_classes = (AllowAny,)

    # get all info
    def get(self, request, slug):
        queryset = BlogComment.objects.filter(blog__slug=slug).order_by('-id')
        serializer = BlogCommentsSerializer(queryset, many=True)
        return Response(serializer.data)


class CreateBlogApi(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aws = Aws()
        sendOtp = Otp()
        try:
            if Blog.objects.filter(title=request.data.get('title')).exists():
                message = "Blog With Title {title} already exist! Please Try again with some other title.".format(
                    title=request.data.get('title'))
                return JsonResponse(error_response(message), status=status.HTTP_400_BAD_REQUEST)
            else:
                if 'feature_image' in request.data and request.data['feature_image']:
                    feature_image = request.data['feature_image']
                    # validate file extension
                    image_name = feature_image.name.split(".")[-1]
                    format = ['jpg', 'jpeg', 'png']

                    if image_name not in format:
                        message = "Invalid image format.Allowed only jpg,jpeg and png"
                        return JsonResponse(error_response(message),
                                            status=status.HTTP_400_BAD_REQUEST)

                blog = Blog.objects.create(
                    expert=request.user,
                    title=request.data.get('title'),
                    slug=request.data.get('slug', None),
                    summary=request.data.get('summary', ""),
                    article_body=request.data.get('article_body', ""),
                    banner_image_url=request.data.get('banner_image_url', ""),
                    feature_image_url=request.data.get('feature_image_url', ""),
                    status=request.data.get('status', 'draft') if (
                            'draft' == request.data.get('status', 'draft') or 'requested' == request.data.get(
                        'status', 'draft')) else 'draft',
                    feature_image=request.data.get('feature_image', '')
                )

            # update all tags with all sort of fail handle
            try:
                blog.tags.remove(*blog.tags.all())
                tags = []
                if 'tags' in request.data and request.data.get('tags') and isinstance(
                        json.loads(request.data.get('tags')), list):
                    for tag in json.loads(request.data.get('tags')):
                        tagObj, created = Tag.objects.get_or_create(tag_name=tag)
                        tags.append(tagObj.id)

                    blog.tags.add(*tags)
            except BaseException as err:
                print(err)

            # update all categories with all sort of fail handle
            try:
                blog.categories.remove(*blog.categories.all())
                categories = []
                if 'categories' in request.data and request.data.get('categories') and isinstance(
                        json.loads(request.data.get('categories')), list):
                    for category in json.loads(request.data.get('categories')):
                        if isinstance(category, dict):
                            categories.append(category.get('id'))
                        print(f'{category=}')
                        categories.append(category)
                    blog.categories.add(*categories)
            except BaseException as err:
                print(err)

            # sending email
            try:
                templateId = None

                if (request.data['status'] == "requested"):
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
                    "params": {'slug': "{0}".format(blog.slug)}
                }
                sendOtp.EmailOtp(task)
            except BaseException as err:
                print(err)

            blog.save()
            serializer = BlogListSerializer(blog, many=False)

            # notify all admins about the new blog create
            notifyService.notifyMobileAppUser(
                title="{user_name} requested new article : {article}".format(user_name=request.user.first_name,
                                                                             article=blog.title),
                body=blog.summary,
                device_tokens=list(
                    UserDeviceToken.objects.filter(user__user_type='admin').values_list('device_token', flat=True)),
                payload={},
                small_img_url=None,
                large_img_url=None
            )

            return JsonResponse(success_response(serializer.data), status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception("Error Occured While Creating Blog : ", exc_info=err)
            # return JsonResponse({
            #     'message': 'Something went wrong',
            #     'error': str(err)
            # },
            #     safe=False,
            #     status=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )
            return JsonResponse(error_response(str(err)),
                                safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )


class UpdateBlogApi(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, blog_id):
        aws = Aws()
        try:
            if not Blog.objects.filter(id=blog_id, expert_id=request.user.id).exists():
                message = "Blog does not exists"
                return JsonResponse(error_response(message), status=status.HTTP_400_BAD_REQUEST)
            else:
                blog = Blog.objects.get(id=blog_id, expert_id=request.user.id)

            if 'feature_image' in request.data and request.data['feature_image']:
                feature_image = request.data['feature_image']
                # validate file extension
                image_name = feature_image.name.split(".")[-1]
                format = ['jpg', 'jpeg', 'png']

                if image_name not in format:
                    message = "Invalid image format.Allowed only jpg,jpeg and png"
                    return JsonResponse(error_response(message),
                                        status=status.HTTP_400_BAD_REQUEST)

            blog.expert = request.user
            blog.title = request.data.get('title', blog.summary)
            blog.slug = request.data.get('slug', blog.slug)
            blog.summary = request.data.get('summary', blog.summary)
            blog.article_body = request.data.get('article_body', blog.article_body)
            blog.status = request.data.get('status', blog.status)
            blog.banner_image_url = request.data.get('banner_image_url', blog.banner_image_url)
            blog.feature_image_url = request.data.get('feature_image_url', blog.feature_image_url)
            # blog.status = request.data.get('status', 'draft') if ('draft' == request.data.get('status', 'draft') or 'requested' == request.data.get('status', 'draft') or blog.status == 'approved') else 'draft'
            blog.feature_image = request.data.get('feature_image', blog.feature_image)
            # update all tags with all sort of fail handle
            try:

                tags = []
                if 'tags' in request.data and request.data.get('tags') and isinstance(
                        json.loads(request.data.get('tags')), list):
                    for tag in json.loads(request.data.get('tags')):
                        tagObj, created = Tag.objects.get_or_create(tag_name=tag)
                        tags.append(tagObj.id)
                    blog.tags.remove(*blog.tags.all())
                    blog.tags.add(*tags)
            except BaseException as err:
                print(err)

            # update all categories with all sort of fail handle
            try:

                categories = []
                if 'categories' in request.data and request.data.get('categories') and isinstance(
                        json.loads(request.data.get('categories')), list):
                    for category in json.loads(request.data.get('categories')):
                        if isinstance(category, dict):
                            categories.append(category.get('id'))
                        categories.append(category)
                    blog.categories.remove(*blog.categories.all())
                    blog.categories.add(*categories)
            except BaseException as err:
                print(err)

            blog.save()
            serializer = BlogListSerializer(blog, many=False)

            return JsonResponse(success_response(serializer.data), status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception("Error Occured While Creating Blog : ", exc_info=err)
            # return JsonResponse({
            #     'message': 'Something went wrong',
            #     'error': str(err)
            # },
            #     safe=False,
            #     status=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )
            return JsonResponse(error_response(str(err)),
                                safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )


class BlogStatusUpdateApi(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, blog_id, blog_status):
        sendOtp = Otp()
        try:
            errMessage = ''
            if Blog.objects.filter(id=blog_id).exists():
                if request.user.user_type == 'admin':
                    blog = Blog.objects.get(id=blog_id)
                    if blog_status == 'approved' or blog_status == 'published':
                        # send notification to expert about his blog status
                        print("notify expert all devices about blog publish")
                        # send notification to expert all devices
                        if UserDeviceToken.objects.filter(user=blog.expert).exists():
                            # sending email
                            try:
                                if (blog_status == 'approved' or blog_status == "published"):
                                    templateId = 31
                                    task = {
                                        "sender": {
                                            "name": "YellowSquash",
                                            "email": "yellowsquash@gmail.com"
                                        },
                                        "to": [
                                            {
                                                "email": "{0}".format(blog.expert.email),
                                                "name": "{0}".format(blog.expert.first_name)
                                            }
                                        ],
                                        "templateId": templateId,
                                        "params": {"fullname": "{0}".format(blog.expert.first_name),
                                                   'article_name': "{0}".format(blog.title),
                                                   'slug': "{0}".format(blog.slug)}
                                    }
                                    sendOtp.EmailOtp(task)
                            except BaseException as err:
                                print(err)
                            notifyService.notifyMobileAppUser(
                                title="Your Article : {article} got {status}".format(article=blog.title,
                                                                                     status=blog_status),
                                body=blog.summary,
                                device_tokens=list(
                                    UserDeviceToken.objects.filter(user=blog.expert).values_list('device_token',
                                                                                                 flat=True)),
                                payload={},
                                small_img_url=None,
                                large_img_url=None
                            )
                elif request.user.user_type == 'expert':
                    if Blog.objects.get(id=blog_id).status != 'approved' or Blog.objects.get(
                            id=blog_id).status != 'published':
                        if blog_status == 'approved' or blog_status == 'published':
                            errMessage = errMessage = "Expert can't approve/publish non approved article !"
                else:
                    errMessage = "This user is not authorized to upadte blog status !"
            else:
                errMessage = "requested blog doesn't exist"

            # if there is any validation issue then stop process and give error response
            if errMessage:
                return JsonResponse({
                    "message": errMessage
                }, status=status.HTTP_400_BAD_REQUEST)

            # admin can update blog status to any
            # expert can update status to any if it is approved or published 
            blog.status = blog_status
            blog.save()

            return JsonResponse({
                "message": "success"
            }, status=status.HTTP_202_ACCEPTED)

        except BaseException as err:
            logger.exception("Error Occured While Creating Blog : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteBlogApi(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, blog_id):
        try:
            if Blog.objects.filter(id=blog_id, expert=request.user).exists():
                Blog.objects.filter(id=blog_id, expert=request.user).delete()
            else:
                return JsonResponse({
                    "message": "user don't have permission to update this requested blog !"
                }, status=status.HTTP_400_BAD_REQUEST)
            message = "Blog deleted successfully"
            return JsonResponse(success_response(message), status=status.HTTP_202_ACCEPTED)
        except BaseException as err:
            logger.exception("Error Occured While Deleting Blog : ", exc_info=err)
            # return JsonResponse({
            #     'message': 'Something went wrong',
            #     'error': str(err)
            # },
            #     safe=False,
            #     status=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )
            return JsonResponse(error_response(str(err)),
                                safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )


class AddBlogComment(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, blog_id):
        sendOtp = Otp()
        blogComment = BlogComment.objects.create(
            user=request.user,
            blog_id=blog_id,
            comment=request.data.get('comment'),
        )
        nestr = re.sub(r'[^a-zA-Z0-9]', r'', Blog.objects.get(id=blog_id).slug)
        # publish new comments on centri for realtime user-exp
        notifyService.centrifugePublish(
            channel=nestr,
            data={
                "command": 'comment',
                "id": blogComment.id,
                "user_id": request.user.id,
                "comment": blogComment.comment,
                "user": request.user.get_user_fullname(),
                "created_at": blogComment.created_at.strftime('%Y-%m-%dT%H:%M:%S')
            }
        )
        # send email on new comment
        # task={  
        #     "sender":{  
        #         "name":"YellowSquash",
        #         "email":"yellowsquash@gmail.com"
        #     },
        #     "to":[  
        #         {  
        #             "email":"{0}".format(blogComment.blog.expert.email),
        #             "name":"{0}".format(blogComment.blog.expert.first_name)
        #         }
        #     ],
        #     "templateId":10,
        #     "params":{}
        # }
        # sendOtp.EmailOtp(task)

        return Response({
            "status": "success"
        })


class UpdateBlogComment(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, blog_comment_id):
        try:
            # validate before update
            if not request.user.user_type == 'customer' or not BlogComment.objects.filter(id=blog_comment_id,
                                                                                          user=request.user).exists():
                raise Exception('current user is not authorized to update this comment')
            else:
                blogComment = BlogComment.objects.get(id=blog_comment_id, user=request.user)
                blogComment.comment = request.data['comment']
                blogComment.save()

            # nestr = re.sub(r'[^a-zA-Z0-9]',r'',Blog.objects.get(id=blogComment.blog.id).slug)
            # publish new comments on centri for realtime user-exp
            # notifyService.centrifugePublish(
            #     channel=nestr,
            #     data={
            #         "id": blogComment.id,
            #         "comment": blogComment.comment,
            #         "user": request.user.get_user_fullname(),
            #         "user_id": request.user.id,
            #         "created_at": blogComment.created_at.strftime('%Y-%m-%dT%H:%M:%S')
            #     }
            # )

            return Response({
                "status": "success"
            })

        except BaseException as err:
            logger.exception("Error Occured While updating Blog comment : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteBlogComment(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, blog_comment_id):
        try:
            # validate before update
            if request.user.user_type == 'customer' and BlogComment.objects.filter(id=blog_comment_id,
                                                                                   user=request.user).exists():
                BlogComment.objects.filter(id=blog_comment_id).delete()
            elif request.user.user_type == 'admin':
                BlogComment.objects.filter(id=blog_comment_id).delete()
            elif request.user.user_type == 'expert' and BlogComment.objects.filter(id=blog_comment_id,
                                                                                   blog__expert_id=request.user).exists():
                BlogComment.objects.filter(id=blog_comment_id).delete()
            else:
                raise Exception('current user is not authorized to delete this comment')

            return Response({
                "status": "success"
            })

        except BaseException as err:
            logger.exception("Error Occured While deleting Blog comment : ", exc_info=err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlogLikeDislike(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, blog_id):
        if BlogLike.objects.filter(user=request.user, blog_id=blog_id).exists():
            BlogLike.objects.filter(user=request.user, blog_id=blog_id).delete()
        else:
            blogLike = BlogLike.objects.create(
                user=request.user,
                blog_id=blog_id,
            )
        return Response({
            "status": "success"
        })


class UserBlogShare(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, blog_id):
        blogSbhare = BlogShare.objects.create(
            user=request.user,
            blog_id=blog_id,
            where=request.data.get('platform'),
        )
        return Response({
            "status": "success"
        })


class BlogGetUpdateDelete(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BlogListSerializer
    queryset = Blog.objects.all()


class BlogLikeShareView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BlogLikeShareViewSerializer
    queryset = BlogStates.objects.all()

    def get(self, request):
        self.get_queryset = self.get_queryset().filter()
        serializer = self.get_serializer(self.get_queryset, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

    def post(self, request):
        queryset = BlogStates.objects.all()
        data = BlogStates.objects.filter(user_id=request.user.id, blog=request.data.get('blog'))
        request.data['user'] = request.user.id

        if data.exists() and not request.data.get('is_shared'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(data.first(), serializer.validated_data)
            nestr = re.sub(r'[^a-zA-Z0-9]', r'', Blog.objects.get(id=request.data['blog']).slug)
            notifyService.centrifugePublish(
                channel=nestr,
                data={
                    "command": 'like',
                    "user_id": request.user.id,
                    "blog": request.data['blog'],
                    "view": request.data['is_view'],
                    "user": request.user.get_user_fullname(),
                    "total_like": BlogStates.objects.filter(is_like="True", blog=request.data['blog']).count(),
                    "total_share": BlogStates.objects.filter(is_shared="True", blog=request.data['blog']).count()
                }
            )

            return JsonResponse(serializer.data, safe=False)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.create(serializer.validated_data)
            nestr = re.sub(r'[^a-zA-Z0-9]', r'', Blog.objects.get(id=request.data['blog']).slug)
            notifyService.centrifugePublish(
                channel=nestr,
                data={
                    "command": 'like',
                    "user_id": request.user.id,
                    "blog": request.data['blog'],
                    "user": request.user.get_user_fullname(),
                    "total_like": BlogStates.objects.filter(is_like="True", blog=request.data['blog']).count(),
                    "total_share": BlogStates.objects.filter(is_shared="True", blog=request.data['blog']).count()
                }
            )
            return JsonResponse(serializer.data, safe=False)


class GlobalSearchBlog(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            queryset = Blog.objects.filter(title__icontains=request.data['searchBy'], status='published').order_by(
                '-updated_at')[:40]
            serializer = GlobalSearchBlogSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        except BaseException as error:
            return JsonResponse({
                'error': str(error)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetSingleBlogApi(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
            serializer = SingleBlogSerializer(blog, many=False)
            return JsonResponse(success_response(serializer.data), status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return JsonResponse(error_response("Blog does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return JsonResponse(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddFavouriteBlog(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, blog_id):
        try:
            user = request.user
            if Blog.objects.filter(id=blog_id, favourite=user).exists():
                # success message
                return Response(success_response("Blog already added to favourite"), status=status.HTTP_200_OK)
            else:
                blog = Blog.objects.get(id=blog_id)
                blog.favourite.add(user)
                blog.save()

                return Response(success_response("Blog added to favourite"), status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response(error_response("Blog does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, blog_id):
        try:
            user = request.user

            blog = Blog.objects.get(id=blog_id)
            blog.favourite.remove(user)
            blog.save()

            return Response(success_response("Blog removed from favourite"), status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response(error_response("Blog does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavouriteBlogList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Blog.objects.filter(favourite__in=[user]).order_by('-created_at')
        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = FavouriteBlogListSerializer(queryset, many=True)
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)