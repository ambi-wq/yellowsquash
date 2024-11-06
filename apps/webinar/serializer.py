import os
from datetime import datetime
from rest_framework import serializers
from apps.user.models import User, UserIntrestOrExpertise
from yellowsquash import settings
from .models import Webinar, Section, WebinarCategory, WebinarSection
from apps.user.serializer import ExpertiseSerializer


class UserIntrestOrExpertiseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')

    class Meta:
        model = UserIntrestOrExpertise
        fields = ['id', 'category']


class ExpertSerializer(serializers.ModelSerializer):
    expertises = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'experties', 'expert_score', 'short_description', 'expertises',
                  'user_img']

    def get_expertises(self, obj):
        return UserIntrestOrExpertiseSerializer(obj.intrested_or_expert_user.all(), many=True).data


class WebinarSerializer(serializers.ModelSerializer):
    expert = ExpertSerializer(read_only=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = ['id', 'title', 'slug', 'meta_keywords', 'video_link', 'description', 'thumbnail_url', 'webinar_date',
                  'start_time', 'end_time', 'expert', 'category']

    def get_category(self, obj):
        webinarCat = WebinarCategory.objects.filter(webinar_id=obj.id).values_list('category__id', 'category__name')
        webinar_cat_data = list()
        for webinar_cat_obj in webinarCat:
            webinar_cat_data.append({
                "id": webinar_cat_obj[0],
                "name": webinar_cat_obj[1]
            })
        return webinar_cat_data[:3]


class WebinarDetailSerializer(serializers.ModelSerializer):
    # speaker_first_name = serializers.CharField(source='speaker_user.first_name')
    # expert = serializers.CharField(source='expert.first_name')

    expert = ExpertSerializer(read_only=True)

    sections = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = ['id', 'title', 'subtitle', 'slug', 'meta_keywords', 'video_link', 'thumbnail_url', 'description',
                  'webinar_date', 'start_time', 'end_time', 'whatsapp_link', 'expert', "status", "sections"]

    def get_sections(self, obj):
        print("obj:", obj)
        # if self.context and self.context['request'] and self.context['request'].query_params and self.context['request'].query_params.get('section_type') and isinstance(self.context['request'].query_params.get('section_type'), str):
        # return WebinarSectionsSerializer(obj.webinarsections_set.filter(section__sectionType__iexact=self.context['request'].query_params.get('section_type')), many=True).data
        # return WebinarSectionsSerializer(obj.webinarsection_set.all(), many=True).data

        return WebinarSectionsSerializer(obj.webinarsection_set.filter(status='Active'), many=True).data


class WebinarSectionsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='section.title')
    content = serializers.SerializerMethodField()

    class Meta:
        model = WebinarSection
        fields = ['id', 'webinar', 'section', 'content', 'displayOrder', 'title', 'status']

    def get_content(self, obj):
        return obj.overiddenContent if obj.overiddenContent else obj.section.content


class WebinarCategoryWiseSerializer(serializers.ModelSerializer):
    expert_name = serializers.SerializerMethodField('get_expert_name')
    expert_pic = serializers.SerializerMethodField('get_expert_pic')
    professional_title = serializers.SerializerMethodField('get_professional_title')
    webinar_day = serializers.SerializerMethodField('get_webinar_day')

    class Meta:
        model = Webinar
        fields = ['id', 'title', 'subtitle', 'slug', 'meta_keywords', 'video_link', 'description', 'thumbnail_url',
                  'webinar_date', 'webinar_day',
                  'start_time', 'end_time', 'expert_name', 'expert_pic', 'professional_title', 'category']

    def get_professional_title(self, program):
        return program.expert.professional_title

    def get_expert_name(self, program):
        name = ""
        if program.expert.first_name:
            name += program.expert.first_name + " "
        if program.expert.last_name:
            name += program.expert.last_name
        return name

    def get_expert_pic(self, program):
        if program.expert.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(program.expert.profile_picture))
            return profile_picture
        return ""

    def get_webinar_day(self, webinar):
        webinar_day = webinar.webinar_date.strftime('%a')
        return webinar_day


class UpcomingWebinarSerializer(serializers.ModelSerializer):
    expert_name = serializers.SerializerMethodField('get_expert_name')
    start_time = serializers.SerializerMethodField('get_start_time')
    webinar_date = serializers.SerializerMethodField('get_webinar_date')
    webinar_date_time = serializers.SerializerMethodField('get_webinar_date_time')

    class Meta:
        model = Webinar
        fields = ['id', 'title', 'expert_name', 'thumbnail_image', 'thumbnail_url', 'webinar_date', 'start_time',
                  'webinar_date_time']

    def get_expert_name(self, webinar):
        name = ""
        if webinar.expert.first_name:
            name += webinar.expert.first_name + " "
        if webinar.expert.last_name:
            name += webinar.expert.last_name
        return name

    def get_start_time(self, webinar):
        start_time = webinar.start_time.strftime('%H:%M %p')
        return start_time

    def get_webinar_date(self, webinar):
        webinar_date = webinar.webinar_date.strftime('%d %b %Y')
        return webinar_date

    def get_webinar_date_time(self, webinar):
        return str(webinar.webinar_date) + " " + str(webinar.start_time)


class ExpertDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField('get_name')
    profile_picture = serializers.SerializerMethodField('get_profile_pic')
    experties = serializers.SerializerMethodField('get_experties')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'professional_title', 'short_description', 'profile_picture', 'experties']

    def get_name(self, user):
        name = ""
        if user.first_name:
            name += user.first_name + " "
        if user.last_name:
            name += user.last_name
        return name

    def get_profile_pic(self, user):
        if user.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(user.profile_picture))
            return profile_picture
        return ""

    def get_experties(self, user):
        experties = ExpertiseSerializer(user.experties, many=True).data
        return experties

    # def get_experties(self, obj):
    #     return UserIntrestOrExpertiseSerializer(obj.intrested_or_expert_user.all(), many=True).data


class GetWebinarDetailSerializer(serializers.ModelSerializer):
    expert = serializers.SerializerMethodField('get_expert')
    webinar_date_time = serializers.SerializerMethodField('get_webinar_date_time')

    class Meta:
        model = Webinar
        fields = ['id', 'title', 'subtitle', 'slug', 'meta_keywords', 'video_link', 'thumbnail_url', 'description',
                  'webinar_date', 'start_time', 'end_time', 'webinar_date_time', 'expert']

    def get_expert(self, webinar):
        expert = ExpertDetailSerializer(webinar.expert, many=False).data
        return expert

    def get_webinar_date_time(self, webinar):
        return str(webinar.webinar_date) + " " + str(webinar.start_time)


class WebinarListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('get_category')
    expert_name = serializers.CharField(source='expert.first_name')
    profile_picture = serializers.SerializerMethodField('get_expert_profile_picture')
    professional_title = serializers.CharField(source='expert.professional_title')
    is_favourite = serializers.SerializerMethodField('get_is_favourite')

    class Meta:
        model = Webinar
        fields = ['id', 'title', 'video_link', 'thumbnail_url', 'webinar_date', 'start_time', 'category',
                  'expert_name', 'profile_picture', 'professional_title', 'is_favourite']

    def get_category(self, obj):
        category = obj.category.values('id', 'name')
        return category

    def get_expert_profile_picture(self, obj):
        if obj.expert.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.expert.profile_picture))
            return profile_picture
        return ""

    def get_is_favourite(self, obj):
        user = self.context.get('user')
        if user in obj.favourite.all():
            return True
        return False
