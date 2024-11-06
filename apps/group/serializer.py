from datetime import datetime, timedelta

from django.db.models import Q
from rest_framework import serializers

from apps.group.models import Group, GroupInvited, GroupRequested, GroupPost, GroupCategory, GroupMembers, \
    GroupPostMedia, GroupPostLike, GroupCategoryMapping, GroupPostComment
from apps.user.models import Category, User

from apps.tinode.tinode import Tinode
import logging

from apps.user.serializer import UserSerializer

logger = logging.getLogger(__name__)


class GroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("id", "name", "about", "rules", "categories", "author_name",
                  "author", "privacy", "cover_image", "post_mode",
                  "status",
                  "members_count",
                  )

    def get_categories(self, obj):
        dat = GroupCategoryMapping.objects.filter(group=obj.id)
        #print(dat)
        return GroupCategoryMappingSerializer(dat, many=True).data

    def get_members_count(self, obj):
        return GroupMembers.objects.filter(group=obj.id).count()

    def get_author_name(self, obj):
        return obj.author.first_name if obj.author.first_name is not None else '' + ' ' + obj.author.last_name if obj.author.last_name is not None else ''


class GroupCategoryMappingSerializer(serializers.ModelSerializer):
    category_title = serializers.SerializerMethodField()

    class Meta:
        model = GroupCategoryMapping
        fields = "__all__"

    def get_category_title(self,obj):
        return GroupCategory.objects.filter(id=obj.category.id).first().category_title


class GroupInvitedSerializerOut(serializers.ModelSerializer):
    #group_name = serializers.CharField(source='group.name')
    group_details = serializers.SerializerMethodField()
    inviter_details = serializers.SerializerMethodField()
    invite_expired = serializers.SerializerMethodField()

    class Meta:
        model = GroupInvited
        fields = "__all__"

    def get_invite_expired(self,obj):
        return datetime.today() > obj.created_on + timedelta(days=30)

    def get_group_details(self,obj):
        return GroupSerializer(obj.group, many=False).data

    def get_inviter_details(self,obj):
        return UserSerializer(obj.invited_by, many=False).data


class GroupRequestedSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    class Meta:
        model = GroupRequested
        fields = "__all__"

    def get_user(self, obj):
        #print('obj.member',obj.member)
        #print('idx',User.objects.get(id=obj.member))
        return UserSerializer(obj.member).data


class GroupRequestedSerializerOut(serializers.ModelSerializer):
    group_name = serializers.CharField(source = 'group.id')

    class Meta:
        model = GroupRequested
        fields = "__all__"


class GroupMembersSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupMembers
        fields = "__all__"


class GroupPostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupPostLike
        fields = "__all__"


class GroupPostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    self_liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = GroupPost
        fields = (
            "group", "member", "added_on", "status", "text",
            "tags", "id",

            "likes", "media", "self_liked", "comment_count"
        )

    def get_likes(self, obj):
        return GroupPostLike.objects.filter(post=obj.id).count()

    def get_media(self, obj):
        return GroupPostMediaSerializer(GroupPostMedia.objects.filter(post=obj.id), many=True).data

    def get_self_liked(self, obj):
        return GroupPostLike.objects.filter(Q(post=obj.id) & Q(member=self.context.get('user_id'))).count() > 0

    def get_comment_count(self, obj):
        return GroupPostComment.objects.filter(Q(post=obj.id)).count()


class GroupCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupCategory
        fields = "__all__"


class GroupPostMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupPostMedia
        fields = "__all__"


class GroupPostCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = GroupPostComment
        fields = "__all__"

    def get_user(self, obj):
        #print('obj.member',obj.member)
        #print('idx',User.objects.get(id=obj.member))
        return UserSerializer(obj.member).data

