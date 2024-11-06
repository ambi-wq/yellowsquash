from rest_framework import serializers
from .models import *


class VideoSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('get_category')
    tags = serializers.SerializerMethodField('get_tags')

    class Meta:
        model = Video
        # exclude = ['expert']
        fields = ('id', 'title','slug', 'thumbnail','upload_video','created_at','updated_at','status','rejection_message','approved_by', 'category','tags')

    def get_category(self, obj):
        try:
            category = VideoCategorySerializer(obj.category,many=True)
            # return obj.category.values_list('name', flat=True)
            return category.data
        except BaseException as err:
            return []

    def get_tags(self, obj):
        try:
            tags = TagSerializer(obj.tags,many=True)
            # return obj.tags.values_list('tag_name', flat=True)
            return tags.data
        except BaseException as err:
            return []


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag_name']


class VideoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']