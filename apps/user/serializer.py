from rest_framework import serializers
from .models import User, UserEducationDetail, Group, FavoriteExpert, ExpertList, CategoryList, UserIntrestOrExpertise, \
    Category, UserDeviceToken, Location, Languages, TimeZone, Expertise, ExpertTeamMember, Role, DegreeCertification
from apps.tinode.tinode import Tinode
import json
import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'mobile', 'title', 'first_name', 'last_name', 'nick_name', 'user_type', 'user_img',
            'email', 'is_verified', 'email_verified', 'mobile_verified', 'created_at', 'last_updated_at', 'status',
            'designation',
            'qualification', 'experience', 'experties', 'fb_link', 'twitter_link', 'linked_link', 'google_link',
            'language', 'professional_title',
            'location', 'video_url', 'short_description', 'password', 'expert_score', 'age', 'gender'
        ]

    def validate(self, request):
        return request

    def create(self, validated_data):
        groupd, is_created = Group.objects.get_or_create(
            defaults={'name': "Default User Group"}
        )
        user = User.objects.create(
            email=self.initial_data.get("email"),
            username=self.initial_data.get("username"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            user_type=validated_data.get("user_type", "customer"),
            mobile=validated_data.get("mobile"),
            user_img=validated_data.get("user_img", None),
            email_verified=True,
            is_verified=True,
            group=groupd
        )
        user.set_password(validated_data.get("password"))

        # insert chat token if available
        try:
            tinodeNew = Tinode()
            token = tinodeNew.CreateUserAndGetToken(
                username=self.initial_data.get("username"),
                password=validated_data.get("password"),
                first_name=validated_data.get("first_name", "User"),  # can't be blank or null
                tags=[validated_data.get("user_type", "customer")],  # can't be blank or null
            )
            if token:
                user.tinode_token = token
                logger.info(token)
            else:
                logger.info("tinode token genration failed for the username : ", self.initial_data.get("username"))
        except BaseException as err:
            logger.exception("Failed getting tinode token : ", exc_info=err)

        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField('get_language')
    timezone = serializers.SerializerMethodField('get_timezone')
    location = serializers.SerializerMethodField('get_location')
    experties = serializers.SerializerMethodField('get_experties')
    is_favorite = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    # degree_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser', 'username', 'mobile', 'title', 'first_name', 'last_name',
                  'nick_name', 'user_type',
                  'user_img', 'email', 'is_verified', 'email_verified', 'mobile_verified', 'created_at',
                  'last_updated_at',
                  'status', 'designation', 'qualification', 'experience', 'experties', 'fb_link', 'twitter_link',
                  'linked_link', 'google_link',
                  'group', 'is_favorite', 'categories', 'professional_title', 'language', 'video_url',
                  'short_description', "location", "is_profile_complete",
                  "expert_score", "profile_picture", "timezone", 'age', 'gender'
                  ]

    def get_is_favorite(self, obj):
        try:
            # for there some api we don't need to use suer for general get calls
            return FavoriteExpert.objects.filter(expert=obj, user_id=self.context.get('user_id')).exists()
        except BaseException as err:
            print(err)
            return False

    def get_categories(self, obj):
        try:
            # return obj.category.values_list('name', flat=True)
            return obj.category.values('id', 'name')
        except BaseException as err:
            return []

    def get_degree_name(self, obj):
        try:
            return obj.certified_user.values('id', 'course_name')
        except BaseException as err:
            print(err)
            return []

    def get_location(self, obj):
        try:
            location = Location.objects.filter(location_id=obj.location_id).values().first()
            return location
        except BaseException as err:
            print(err)
            return {}

    def get_timezone(self, obj):
        try:
            timezone = TimeZone.objects.filter(timezone_id=obj.timezone_id).values().first()
            return timezone
        except BaseException as err:
            print(err)
            return {}

    def get_language(self, obj):
        try:
            serializer = LanguageSerializer(obj.language, many=True)
            return serializer.data
        except BaseException as err:
            print(err)
            return []

    def get_experties(self, obj):
        try:
            serializer = ExpertiseSerializer(obj.experties, many=True)
            return serializer.data
        except BaseException as err:
            print(err)
            return []


class ExpertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertList

        # fields = ['id', 'username', 'mobile', 'title', 'first_name', 'last_name', 'nick_name', 'user_type',
        #           'user_img', 'email', 'is_verified', 'email_verified', 'mobile_verified', 'created_at',
        #           'last_updated_at',
        #           'status', 'designation', 'qualification', 'experience', 'experties', 'fb_link', 'twitter_link',
        #           'linked_link', 'google_link',
        #           'group', 'is_favorite', 'categories', 'short_description', 'professional_title', "expert_score",
        #           "profile_picture"]
        fields = ['id', 'username', 'mobile', 'title', 'first_name', 'last_name', 'nick_name', 'user_type',
                  'user_img', 'email', 'is_verified', 'email_verified', 'mobile_verified', 'created_at',
                  'last_updated_at',
                  'status', 'designation', 'qualification', 'experience', 'fb_link', 'twitter_link',
                  'linked_link', 'google_link',
                  'group', 'is_favorite', 'categories', 'short_description', 'professional_title', "expert_score",
                  "profile_picture"]


class ExpertUserSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'mobile', 'title', 'first_name', 'last_name', 'nick_name', 'user_type',
                  'user_img', 'email', 'is_verified', 'email_verified', 'mobile_verified', 'created_at',
                  'last_updated_at',
                  'status', 'designation', 'qualification', 'experience', 'experties', 'fb_link', 'twitter_link',
                  'linked_link', 'google_link',
                  'group', 'categories', 'short_description', 'professional_title', 'expert_score', "profile_picture"]

    def get_categories(self, obj):
        return list(obj.category.values_list('name', flat=True))


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class FavoriteExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteExpert
        fields = "__all__"


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryList
        # fields = ("id", "name", "logo", "is_selected")
        fields = ("id", "name")


class UserIntrestOrExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserIntrestOrExpertise
        fields = "__all__"


class UserCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')

    class Meta:
        model = UserIntrestOrExpertise
        fields = ('category_name',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class UserEducationDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField('get_course_name')

    class Meta:
        model = UserEducationDetail
        # fields = "__all__"
        fields = ['id', 'institution_name', 'completion_year', 'description', 'certificate_doc', 'certificate_doc_url',
                  'user', 'course_name']

    def get_course_name(self, obj):
        data = DegreeCertification.objects.filter(degree_id=obj.course_name_id).values('degree_id',
                                                                                       'degree_name').first()
        return data


class UserDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceToken
        fields = "__all__"


class GlobalSearchUserSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = ExpertList
        fields = ['id', 'first_name', 'last_name', 'user_type', 'user_img', 'category', 'professional_title',
                  'short_description', 'expert_score']

    def get_category(self, obj):
        try:
            return list(obj.category.values_list('name', flat=True))
        except BaseException as err:
            return []


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = "__all__"


class TimezoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeZone
        fields = "__all__"


class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = "__all__"


class ExpertTemMemberSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)
    is_expert = serializers.SerializerMethodField('get_is_expert')

    class Meta:
        model = ExpertTeamMember
        # exclude = ['user']
        fields = ['team_member_id', 'role', 'name', 'phone', 'email', 'is_active', 'is_expert']

    def get_is_expert(self, obj):
        return False


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class DegreeCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeCertification
        fields = "__all__"


class CustomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ExpertSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_expert_name')
    category = serializers.SerializerMethodField('get_category')
    is_favourite = serializers.SerializerMethodField('get_is_favourite')

    class Meta:
        model = User
        fields = ['id', 'name', 'profile_picture', 'short_description', 'designation', 'professional_title', 'category',
                  'is_favourite']

    def get_expert_name(self, user):
        name = ""
        if user.first_name:
            name += user.first_name + " "
        if user.last_name:
            name += user.last_name
        return name

    def get_category(self, user):
        category = user.category.values('id', 'name')
        return category

    def get_is_favourite(self, user):
        current_user = self.context.get('user')
        is_favourite = FavoriteExpert.objects.filter(user=current_user, expert=user).exists()
        return is_favourite


class ExpertDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_expert_name')
    category = serializers.SerializerMethodField('get_category')
    qualification =serializers.SerializerMethodField('get_qualification')

    class Meta:
        model = User
        fields = ['id','name','professional_title','profile_picture', 'short_description','category','qualification']

    def get_expert_name(self, user):
        name = ""
        if user.first_name:
            name += user.first_name + " "
        if user.last_name:
            name += user.last_name
        return name

    def get_category(self, user):
        category = user.category.values('id', 'name')
        return category

    def get_qualification(self,user):
        # return UserEducationDetailSerializer(user,many=True).data
        education = UserEducationDetail.objects.filter(user=user)
        return UserEducationDetailSerializer(education,many=True).data