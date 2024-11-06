import os

from rest_framework import serializers
from apps.blog.models import *
from apps.videos.models import *
from yellowsquash import settings


class BlogListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('get_category')
    tags = serializers.SerializerMethodField('get_tags')
    is_favourite = serializers.SerializerMethodField('get_is_favourite')
    expert_name = serializers.CharField(source='expert.first_name')
    profile_picture = serializers.SerializerMethodField('get_expert_profile_picture')

    class Meta:
        model = Blog
        fields = ['id', 'title', 'banner_image_url', 'category', 'tags', 'is_favourite', 'expert_name',
                  'profile_picture']

    def get_category(self, obj):
        category = obj.categories.values('id', 'name')
        return category

    def get_tags(self, obj):
        tags = obj.tags.values('id', 'tag_name')
        return tags

    def get_is_favourite(self, obj):
        user = self.context.get('user')
        if user in obj.favourite.all():
            return True
        return False

    def get_expert_profile_picture(self, obj):
        if obj.expert.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.expert.profile_picture))
            return profile_picture
        return ""


class VideoListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('get_category')
    tags = serializers.SerializerMethodField('get_tags')
    is_favourite = serializers.SerializerMethodField('get_is_favourite')
    expert_name = serializers.CharField(source='expert.first_name')
    profile_picture = serializers.SerializerMethodField('get_expert_profile_picture')

    class Meta:
        model = Video
        fields = ['id', 'title', 'thumbnail', 'upload_video', 'category', 'tags', 'is_favourite', 'expert_name',
                  'profile_picture']

    def get_category(self, obj):
        category = obj.category.values('id', 'name')
        return category

    def get_tags(self, obj):
        tags = obj.tags.values('id', 'tag_name')
        return tags

    def get_is_favourite(self, obj):
        user = self.context.get('user')
        if user in obj.favourite.all():
            return True
        return False

    def get_expert_profile_picture(self, obj):
        if obj.expert.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.expert.profile_picture))
            return profile_picture
        return ""
