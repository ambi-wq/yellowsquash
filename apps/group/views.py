import os
from datetime import datetime, timedelta

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, Prefetch, Value
from django.db.models.functions import Concat
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from jinja2.utils import F

from apps.group.models import GroupCategory, Group, GroupMembers, GroupPost, GroupRequested, GroupInvited, \
    GroupCategoryMapping, GroupAdmin, GroupPostComment
from apps.group.serializer import GroupSerializer, GroupCategorySerializer, GroupPostSerializer, \
    GroupRequestedSerializer, GroupMembersSerializer, GroupRequestedSerializerOut, GroupPostLikeSerializer, \
    GroupInvitedSerializerOut, GroupPostMediaSerializer, GroupPostCommentSerializer
from apps.user.serializer import UserSerializer
from yellowsquash import settings
from itertools import chain

from apps.user.models import Category, FavoriteExpert
from rest_framework import generics, status
from rest_framework.response import Response
# from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
import logging
import json
from apps.common_utils.Aws import Aws, AwsFilePath
from apps.user.models import User
from django.views.decorators.csrf import csrf_exempt
import random, string
from apps.tinode.tinode import Tinode
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)


class ListCategories(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return GroupCategory.objects.all()

    @never_cache
    def get(self, request):
        queryset = self.get_queryset()

        serializer = GroupCategorySerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class CreateGroup(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        #try:
            file_upload_path = AwsFilePath.GroupCoverImage(
                user_id=request.user.id,
                file_name=request.FILES['cover_image'].name,
            )

            cover_image_url = Aws().upload_file(request.FILES['cover_image'], file_upload_path)

            data = {'name': request.data['name'], 'about': request.data['about'], 'rules': request.data['rules'],
                    'privacy' : request.data['privacy'], 'cover_image': cover_image_url,
                    'author': request.user.id}

            categories = request.data['categories'].split(',')

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # request.data._mutable = False
            data2 = serializer.data
            print(data2)
            group = Group.objects.get(id=int(data2['id']))
            for c in categories:
                gcm = GroupCategoryMapping()
                gcm.group = group
                gcm.category = GroupCategory.objects.get(id=int(c))
                gcm.save()

            return JsonResponse(data2,safe=False, status=status.HTTP_201_CREATED)
        # except BaseException as err:
        #     print(err)
        #     return JsonResponse({
        #         'message': 'Something went wrong',
        #         'error': str(err)
        #     },
        #         safe=False,
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )


class MyGroups(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, id):
        return Group.objects.filter(Q(author=id)  & Q(status='approved'))

    @never_cache
    def get(self, request):
        queryset = self.get_queryset(request.user.id)

        serializer = GroupSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class JoinedGroups(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, id):
        groups = GroupMembers.objects.filter(member=id).values_list('group', flat=True)
        return Group.objects.filter(Q(id__in=groups))

    @never_cache
    def get(self, request):
        queryset = self.get_queryset(request.user.id)

        serializer = GroupSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class GetGroupDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, id):
        return Group.objects.filter(id=id).first()

    @never_cache
    def get(self, request, id):
        queryset = self.get_queryset(id)

        serializer = GroupSerializer(
            queryset,
            many=False,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class EditGroup(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        try:
            group = Group.objects.get(id=request.data.get('group'))

            group.name = request.data.get('name')
            group.about = request.data.get('about')
            group.rules = request.data.get('rules')

            if 'cover_image' in request.FILES and request.FILES['cover_image'] is not None:
                print('mod cover_image')
                file_upload_path = AwsFilePath.GroupCoverImage(
                    user_id=request.user.id,
                    file_name=request.FILES['cover_image'].name,
                )
                group.cover_image = Aws().upload_file(request.FILES['cover_image'], file_upload_path)

            group.save()

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


class RemoveGroup(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        try:
            group = Group.objects.get(id=request.data.get('group'))

            group.status = 'removed'
            group.save()

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


class LeaveGroup(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            group_member = GroupMembers.objects.filter(member=request.user.id, group=request.data.get('group'))
            if group_member.exists():
                group_member.delete()
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


class CreateGroupPost(generics.CreateAPIView):
    serializer_class = GroupPostSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:

            data = {'group': request.data['group'], 'text': request.data['text'], 'tags': request.data['tags'],
                    'member': request.user.id}

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            sdata = serializer.data

            for x in request.FILES.getlist('files'):
                file_upload_path = AwsFilePath.GroupPostMedia(
                    user_id=request.user.id,
                    post_id = sdata['id'],
                    file_name= x.name,
                )
                img_url = Aws().upload_file(x, file_upload_path)

                data = {'post': sdata['id'], 'media': img_url}

                serializer = GroupPostMediaSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

            return JsonResponse(GroupPostSerializer(GroupPost.objects.get(id=sdata['id'])).data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PendingApprovalGroupPost(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,  user_id):
        return GroupPost.objects.filter(Q(group__author=user_id) & Q(status='pending'))

    @never_cache
    def get(self, request):
        queryset = self.get_queryset(request.user.id)

        serializer = GroupPostSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class ApprovalGroupPost(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,  user_id, post_id):
        return GroupPost.objects.filter(Q(group__author=user_id) & Q(id=post_id)).first()

    @never_cache
    def put(self, request):
        queryset = self.get_queryset(request.user.id, request.data["post"])

        queryset.status = request.data["status"]
        queryset.status_changed_by = User.objects.get(id=request.user.id)
        queryset.status_modified_on = datetime.now()

        queryset.save()

        return JsonResponse(
            data={'message': 'success'},
            status=status.HTTP_201_CREATED
        )


class LikeGroupPost(generics.CreateAPIView):
    serializer_class = GroupPostLikeSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        try:
            data = {'post': request.data['post'], 'member': request.user.id}

            serializer = self.get_serializer(data=data)
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


class JoinGroup(generics.CreateAPIView):
    serializer_class = GroupRequestedSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            data = {'group': request.data['group'], 'member': request.user.id}

            serializer = self.get_serializer(data=data)
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


class PendingApprovalGroup(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,  user_id):
        return GroupRequested.objects.filter(Q(group__author=user_id) & Q(status='pending'))

    @never_cache
    def get(self, request):
        queryset = self.get_queryset(request.user.id)

        serializer = GroupRequestedSerializerOut(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class ApproveJoinGroup(generics.CreateAPIView):
    serializer_class = GroupMembersSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, req_id):
        return GroupRequested.objects.filter(id=req_id).first()

    def put(self, request, *args, **kwargs):
        try:
            requested_group = self.get_queryset(request.data['req_id'])

            requested_group.status = request.data['status'] # approved, rejected, pending
            requested_group.status_modified_by = User.objects.get(id=request.user.id)

            requested_group.save()

            if request.data['status'] == 'approved':
                data = {'group': requested_group.group.id, 'member': requested_group.member.id}

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                return JsonResponse({
                    'message': 'Request has been Approved'
                },
                    safe=False,
                    status=status.HTTP_201_CREATED
                )
            else:
                return JsonResponse({
                    'message': 'Request has been Rejected',
                },
                    safe=False,
                    status=status.HTTP_201_CREATED
                )
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InviteToGroup(generics.CreateAPIView):
    serializer_class = GroupPostLikeSerializer
    permission_classes = (IsAuthenticated,)

    count = 0
    def invite(self, users, group, invited_by):
        for u in users:
            if GroupInvited.objects.filter(Q(member=u) & Q(group=group)).count() > 0 or \
                    GroupMembers.objects.filter(Q(member=u) & Q(group=group)).count() > 0:
                continue  # skip inviting this user

            gi = GroupInvited()
            gi.group = group
            gi.invited_by = invited_by
            gi.member = User.objects.get(id=u)
            gi.save()
            self.count = self.count + 1

    def put(self, request, *args, **kwargs):
        try:
            group_id = request.data['group_id']
            users = request.data['user_ids']
            groups = request.data['group_ids']
            # categories = request.data['category_ids']

            group = Group.objects.get(id=group_id)
            invited_by = User.objects.get(id=request.user.id)

            self.invite(users, group, invited_by)

            for g in groups:
                members = GroupMembers.objects.filter(group=g).values_list('member_id', flat=True)
                self.invite(members, group, invited_by)

            return JsonResponse({
                'message':'Invited - ' + str(self.count)
            }, status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)

            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PendingInviteGroup(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,  user_id):
        return GroupInvited.objects.filter(Q(member=user_id) & Q(status='pending'))

    @never_cache
    def get(self, request):

        queryset = self.get_queryset(request.user.id)
        print(queryset.query)
        serializer = GroupInvitedSerializerOut(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class ApproveInviteGroup(generics.CreateAPIView):
    serializer_class = GroupMembersSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, req_id):
        return GroupInvited.objects.filter(id=req_id).first()

    def put(self, request, *args, **kwargs):
        try:
            requested_group = self.get_queryset(request.data['req_id'])

            requested_group.status = request.data['status'] # approved, rejected, pending
            requested_group.status_modified_by = User.objects.get(id=request.user.id)

            requested_group.save()

            if request.data['status'] == 'approved':
                data = {'group': requested_group.group.id, 'member': request.user.id}

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                print(serializer.data)
                return JsonResponse({
                    'message': 'Request has been Approved'
                },
                    safe=False,
                    status=status.HTTP_201_CREATED
                )
            else:
                return JsonResponse({
                    'message': 'Request has been Rejected',
                },
                    safe=False,
                    status=status.HTTP_201_CREATED
                )
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchGroups(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, text):
        return Group.objects.filter(Q(name__icontains=text) & Q(status='approved'))[:5]

    @never_cache
    def get(self, request, text):
        queryset = self.get_queryset(text)

        serializer = GroupSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class SearchUsers(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, text):
        obj = User.objects.all().annotate(text=Concat("first_name", Value(' '), "last_name")).filter(Q(text__icontains=text) | Q(email__icontains=text))[:5]
        return obj

    @never_cache
    def get(self, request, text):
        queryset = self.get_queryset(text)

        serializer = UserSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class MyPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, id, group_id):
        obj = GroupPost.objects.filter(Q(group=group_id) & Q(member=id) & Q(status='approved'))
        return obj

    @never_cache
    def get(self, request, group):
        queryset = self.get_queryset(request.user.id, group)

        serializer = GroupPostSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class GroupPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, group_id):
        obj = GroupPost.objects.filter(Q(group=group_id) & Q(status='approved'))
        return obj

    @never_cache
    def get(self, request, group, page_no, page_size):
        queryset = self.get_queryset(group)

        paginator = Paginator(queryset, page_size)
        queryset = paginator.page(page_no)

        serializer = GroupPostSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        out_data = {
            'data': data,
            'current': int(page_no),
            'pages': paginator.num_pages
        }
        return JsonResponse(out_data, safe=False)


class GetGroupsForCategories(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, categories):
        group_list = GroupCategoryMapping.objects.filter(category__in=categories).values_list('group', flat=True).distinct()
        return Group.objects.filter(Q(id__in=group_list)  & Q(status='approved')).distinct()

    @never_cache
    def post(self, request):
        queryset = self.get_queryset(request.data['categories'])

        serializer = GroupSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class GetGroupMembers(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_members(self, group_id, top):
        members = GroupMembers.objects.filter(group=group_id).values_list('member', flat=True)

        obj = User.objects.filter(id__in=members)
        #print('opx', obj)
        count = obj.count()
        obj = obj[:] if top is None or top == -1 else obj[:top]
        return (obj, count)

    def get_admins(self, group_id, top):
        admins = GroupAdmin.objects.filter(group=group_id).values_list('member', flat=True)
        obj = User.objects.filter(id__in=admins)
        count = obj.count()
        obj = obj[:] if top is None or top == -1 else obj[:top]
        obj = obj
        return (obj, count)

    def get_pending_requests(self, group_id, top):
        obj = GroupRequested.objects.filter(Q(group=group_id) & Q(status='pending'))
        count = obj.count()
        obj = obj[:] if top is None or top == -1 else obj[:top]
        return (obj, count)

    @never_cache
    def get(self, request, group_id, top_members, top_admins, top_invites):

        members, mem_count = self.get_members(int(group_id), int(top_members))
        admins, admin_count = self.get_admins(int(group_id), int(top_admins))
        requested, req_count = self.get_pending_requests(int(group_id), int(top_invites))

        serializer_r = GroupRequestedSerializer(
            requested,
            many=True,
            context={'user_id': request.user.id}
        )

        serializer_m = UserSerializer(
            members,
            many=True,
            context={'user_id': request.user.id}
        )

        serializer_a = UserSerializer(
            admins,
            many=True,
            context={'user_id': request.user.id}
        )

        author = UserSerializer(
            Group.objects.filter(id=int(group_id)).first().author,
            many=False,
            context={'user_id': request.user.id}
        )

        dat = serializer_a.data
        dat.insert(0, author.data)
        data = {'members': serializer_m.data, 'admins': dat, 'requested': serializer_r.data,
                'total_members': mem_count, 'total_admins': admin_count + 1, 'total_requested': req_count}
        # admin_count + 1 for author here
        return JsonResponse(data, safe=False)


class RemovePost(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        try:
            post = GroupPost.objects.get(id=request.data.get('post'))

            post.status = 'rejected'
            post.save()

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


class DiscoverGroups(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, top):
        experts = User.objects.filter(user_type='expert').values_list('id', flat=True)
        res = Group.objects.exclude(author__in=experts).order_by('-created_on')
        return res[:top] if top > -1 else res

    @never_cache
    def get(self, request, top):
        queryset = self.get_queryset(int(top))

        serializer = GroupSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class ExpertGroups(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, top):
        experts = User.objects.filter(user_type='expert').values_list('id', flat=True)
        res = Group.objects.filter(author__in=experts).order_by('-created_on')
        print('aaae >-1' if top > -1 else 'res')
        return res[:top] if top > -1 else res

    @never_cache
    def get(self, request, top):
        queryset = self.get_queryset(int(top))

        serializer = GroupSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class ForYouPosts(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, user_id, max):
        groups = list(chain(GroupMembers.objects.filter(member=user_id).values_list('id', flat=True),
                            Group.objects.filter(author=user_id).values_list('id', flat=True)))
        obj = GroupPost.objects.filter(Q(group__in= groups) & Q(status='approved'))[:max]
        return obj

    @never_cache
    def get(self, request,  page_no, page_size, max):
        queryset = self.get_queryset(request.user.id, int(max))

        paginator = Paginator(queryset, page_size)
        queryset = paginator.page(page_no)

        serializer = GroupPostSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        out_data = {
            'data': data,
            'current': int(page_no),
            'pages': paginator.num_pages
        }
        return JsonResponse(out_data, safe=False)


class CreateGroupComment(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupPostCommentSerializer

    @never_cache
    def put(self, request, *args, **kwargs):
        try:
            print('xxee')
            data = {'post': request.data['post'], 'comment': request.data['comment'],
                    'parent_comment': request.data['parent_comment'], 'member': request.user.id}

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

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


class GetPostComments(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, post):
        return GroupPostComment.objects.filter(post=post)

    @never_cache
    def get(self, request, post):
        queryset = self.get_queryset(int(post))

        serializer = GroupPostCommentSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data

        return JsonResponse(data, safe=False)


class RemoveMemberGroup(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            group_member = GroupMembers.objects.filter(member=request.data.get('member'), group=request.data.get('group'))
            if group_member.exists():
                group_member.delete()
            else:
                raise Exception('Given Criteria does not match')
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
