import os

from django.conf import settings
from rest_framework import serializers
from .models import *
from apps.user.serializer import CategoryListSerializer, ExpertiseSerializer


class BlogCommentsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = BlogComment
        fields = ('id', 'comment', 'user', 'user_id', 'created_at')

    def get_user(self, obj):
        name = ""
        if obj.user.title:
            name += obj.user.title + " "
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name + " "
        return name


class BlogListSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    expert_id = serializers.IntegerField(source='expert.id')

    class Meta:
        model = Blog
        fields = (
            'id', 'title', 'summary', 'feature_image_url', 'article_body', 'slug', 'writer', 'categories',
            'likes_count',
            'shares_count', 'views_count',
            'status', 'created_at', 'updated_at', 'expert_id', 'feature_image')

    def get_categories(self, obj):
        try:
            return CategoryListSerializer(obj.categories, many=True).data
            # .values_list('name' , flat=True)
        except BaseException as err:
            return []

    def get_likes_count(self, obj):
        try:
            return obj.blogstates_set.filter(blog=obj.id, is_like=True).count()
        except BaseException as err:
            return 0

    def get_shares_count(self, obj):
        try:
            return obj.blogstates_set.filter(blog=obj.id, is_shared=True).count()
        except BaseException as err:
            return 0

    def get_views_count(self, obj):
        try:
            return obj.blogstates_set.filter(blog=obj.id, is_view=True).count()
        except BaseException as err:
            return 0

    def get_writer(self, obj):
        name = ""
        try:
            expert = obj.expert
            if expert.title:
                name += expert.title + " "
            if expert.first_name:
                name += expert.first_name + " "
            if expert.last_name:
                name += expert.last_name + " "
        except BaseException as err:
            print(err)

        return name


class BlogDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    expert_id = serializers.IntegerField(source='expert.id')
    expert_img = serializers.CharField(source='expert.user_img')
    expert_short_description = serializers.CharField(source='expert.short_description')
    expert_experties = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    expert_name = serializers.SerializerMethodField('get_expert_name')
    expert_professional_title = serializers.SerializerMethodField('get_expert_professional_title')
    expert_profile_picture = serializers.SerializerMethodField('get_expert_profile_picture')

    class Meta:
        model = Blog
        fields = (
        'id', 'title', 'summary', 'feature_image', 'feature_image_url', 'banner_image_url', 'article_body', 'slug',
        'writer',
        'categories', 'tags', 'views_count', 'likes_count', 'shares_count', 'comments', 'comments_count', 'approved_by',
        'status',
        'created_at', 'updated_at', 'expert_id', 'expert_img', 'expert_short_description', 'expert_experties',
        'expert_name', 'expert_professional_title', 'expert_profile_picture')

    def get_categories(self, obj):
        try:
            return CategoryListSerializer(obj.categories, many=True).data
            # return obj.categories.values_list('name' , flat=True)
        except BaseException as err:
            return []

    def get_tags(self, obj):
        try:
            return obj.tags.values_list('tag_name', flat=True)
        except BaseException as err:
            return []

    def get_views_count(self, obj):
        try:
            # return obj.blogview_set.count()
            return BlogView.objects.filter(blog=obj).count()
        except BaseException as err:
            return 0

    def get_likes_count(self, obj):
        try:
            # return obj.blogstates_set.filter(is_like=True).count()
            return BlogLike.objects.filter(blog=obj).count()
        except BaseException as err:
            return 0

    def get_comments(self, obj):
        # return []
        # try:
        #     return BlogCommentsSerializer(obj.blogcomment_set, many=True).data
        # except BaseException as err:
        #     print(err)
        try:
            comment = BlogComment.objects.filter(blog=obj)
            return BlogCommentsSerializer(comment, many=True).data
        except BaseException as err:
            print(err)
            return []

    def get_comments_count(self, obj):
        # return 0
        # try:
        #     return obj.blogcomment_set.count()
        # except BaseException as err:
        #     return 0
        try:
            return BlogComment.objects.filter(blog=obj).count()
        except BaseException as err:
            print(err)
            return 0

    def get_shares_count(self, obj):
        try:
            # return obj.blogstates_set.filter(is_shared=True).count()
            return BlogShare.objects.filter(blog=obj).count()
        except BaseException as err:
            return 0

    def get_writer(self, obj):
        name = ""
        if obj.expert.title:
            name += obj.expert.title + " "
        if obj.expert.first_name:
            name += obj.expert.first_name + " "
        if obj.expert.last_name:
            name += obj.expert.last_name + " "
        return name

    def get_expert_experties(self, obj):
        try:
            # return obj.expert.category.values_list('name', flat=True)
            return ExpertiseSerializer(obj.expert.experties, many=True).data
        except BaseException as err:
            print(err)
            return []

    def get_expert_name(self, obj):
        name = ""
        if obj.expert.first_name:
            name += obj.expert.first_name + " "
        if obj.expert.last_name:
            name += obj.expert.last_name + " "
        return name

    def get_expert_professional_title(self, obj):
        return obj.expert.professional_title

    def get_expert_profile_picture(self, obj):
        if obj.expert.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.expert.profile_picture))
            return profile_picture
        return ""


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'tag_name')


class GlobalSearchBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('id', 'title', 'slug', 'feature_image_url', 'expert', 'categories', 'expert', 'summary')


class BlogLikeShareViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogStates
        fields = ('id', 'user', 'blog', 'is_like', 'is_view', 'is_shared')


class SingleBlogSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField('get_categories')
    tags = serializers.SerializerMethodField('get_tags')

    class Meta:
        model = Blog
        fields = ['id', 'title', 'summary', 'categories', 'tags', 'feature_image', 'article_body', 'expert']

    def get_categories(self, obj):
        try:
            return CategoryListSerializer(obj.categories, many=True).data
            # return obj.categories.values_list('name' , flat=True)
        except BaseException as err:
            return []

    def get_tags(self, obj):
        try:
            return TagsSerializer(obj.tags, many=True).data
        except BaseException as err:
            return []
