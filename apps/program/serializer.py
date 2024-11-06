import os
from datetime import datetime

from django.db.models import F, Sum
from rest_framework import serializers
from apps.user.models import Category, User
from apps.user.serializer import CustomCategorySerializer
from yellowsquash import settings
from .models import Program, ProgramCategory, UserProgramList, Review, FrequentlyAskedQuestion, \
    ProgramBatchUser, FavoriteProgram, \
    ProgramBatch, ProgramBatchSession, ProgramBatchSessionResource, ProgramTask, ActionTaskUserProgram, LevelTracker, \
    ProgramLevelTracker, ProgramLevelValue, ProgramLevelValueType, ProgramSymptomTrackerValue, \
    ProgramSymptomTrackerValueDate, Overview
from apps.tinode.tinode import Tinode
import logging

logger = logging.getLogger(__name__)


class ProgramSerializer(serializers.ModelSerializer):
    expert_first_name = serializers.CharField(source='expert.first_name')
    expert_last_name = serializers.CharField(source='expert.last_name')
    batch_id = serializers.SerializerMethodField()
    upcoming_session_id = serializers.SerializerMethodField()
    upcoming_session_start_date = serializers.SerializerMethodField()
    upcoming_session_start_time = serializers.SerializerMethodField()
    offer_price = serializers.SerializerMethodField()
    session_count = serializers.SerializerMethodField()
    meet_link = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = (
            "id", "title", "rating", "intro_video_url", "image_url", "expert", "expert_first_name", "expert_last_name",
            "auther",
            "html_description", "offer_price", "price", "session_count", "duration_in_weeks", "start_date", "status",
            "batch_id", "upcoming_session_id",
            "upcoming_session_start_date", "upcoming_session_start_time", "meet_link", "is_subscribed", 'speciality')

    def get_batch_id(self, obj):
        batch_id = obj.get_current_batch_id()

        if not batch_id:
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    batch_id = ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                               programBatch__program_id=obj.id).first().programBatch_id

        return batch_id

    def get_upcoming_session_id(self, obj):
        batch_id = obj.get_current_batch_id()

        if not batch_id:
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    batch_id = ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                               programBatch__program_id=obj.id).first().programBatch_id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id,
                                                                  session_date__gte=datetime.today().strftime(
                                                                      '%Y-%m-%d'))
        if programBatchSessions.exists():
            return programBatchSessions.order_by('session_date').first().id
        else:
            return None

    def get_upcoming_session_start_date(self, obj):
        batch_id = obj.get_current_batch_id()

        if not batch_id:
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    batch_id = ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                               programBatch__program_id=obj.id).first().programBatch_id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id,
                                                                  session_date__gte=datetime.today().strftime(
                                                                      '%Y-%m-%d'))
        if programBatchSessions.exists():
            return programBatchSessions.order_by('session_date').first().session_date
        else:
            return None

    def get_upcoming_session_start_time(self, obj):
        batch_id = obj.get_current_batch_id()

        if not batch_id:
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    batch_id = ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                               programBatch__program_id=obj.id).first().programBatch_id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id,
                                                                  session_date__gte=datetime.today().strftime(
                                                                      '%Y-%m-%d'))
        if programBatchSessions.exists():
            return programBatchSessions.order_by('session_date').first().start_time
        else:
            return None

    def get_session_count(self, obj):
        batch_id = obj.get_current_batch_id()

        if not batch_id:
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    batch_id = ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                               programBatch__program_id=obj.id).first().programBatch_id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id)
        if programBatchSessions.exists():
            return programBatchSessions.count()
        else:
            return 0

    def get_offer_price(self, obj):
        price = str(obj.get_current_batch_offer_price())

        if not obj.get_current_batch_id():
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                       programBatch__program_id=obj.id).first().programBatch.offer_price:
                        price = str(ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                                    programBatch__program_id=obj.id).first().programBatch.offer_price)

        return price

    def get_meet_link(self, obj):
        try:
            return ProgramBatch.objects.get(id=obj.get_current_batch_id()).meet_link
        except BaseException as err:
            return None

    def get_start_date(self, obj):
        start_date = ""
        batch_id = self.get_batch_id(obj)

        if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                self.context.get('user_id'), int) and ProgramBatchUser.objects.filter(programBatch__program_id=obj.id,
                                                                                      user__id=self.context.get(
                                                                                          'user_id')).exists():
            if ProgramBatchUser.objects.filter(programBatch__program_id=obj.id, user__id=self.context.get(
                    'user_id')).first().programBatch.batch_start_date != None:
                start_date = str(ProgramBatchUser.objects.filter(programBatch__program_id=obj.id,
                                                                 user__id=self.context.get(
                                                                     'user_id')).first().programBatch.batch_start_date)
        else:
            if (ProgramBatch.objects.filter(id=batch_id).exists()):
                programBatch = ProgramBatch.objects.filter(id=batch_id).first()
                start_date = str(programBatch.batch_start_date)
        return start_date

    def get_is_subscribed(self, obj):
        is_subscribed = 'inactive'
        if ((hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and
             isinstance(self.context.get('user_id'), int)) and (
                ProgramBatchUser.objects.filter(user__id=self.context.get('user_id'),
                                                programBatch__program__id=obj.id).exists())):
            print('obj', )
            batch_id = obj.get_current_batch_id()
            data = ProgramBatchUser.objects.filter(user__id=self.context.get('user_id'),
                                                   programBatch__id=obj.get_current_batch_id()).values('status')
            print('dat', data.query)
            if len(data) > 0:
                if data[0]['status'] == "active":
                    is_subscribed = "active"
                    if data[0]['status'] == "payment_under_review":
                        self.is_subscribed = "payment_under_review"
        print('sub:', is_subscribed)
        return is_subscribed


class ProgramBatchSerializer(serializers.ModelSerializer):
    # expert_first_name = serializers.CharField(source='expert.first_name')
    # expert_last_name = serializers.CharField(source='expert.last_name')
    batch_id = serializers.IntegerField(source="id")
    upcoming_session_id = serializers.SerializerMethodField()
    upcoming_session_start_date = serializers.SerializerMethodField()
    upcoming_session_start_time = serializers.SerializerMethodField()
    # offer_price = serializers.SerializerMethodField()
    session_count = serializers.SerializerMethodField()
    # meet_link = serializers.SerializerMethodField()
    # start_date = serializers.SerializerMethodField()
    # is_subscribed = serializers.SerializerMethodField()

    id = serializers.IntegerField(source="program.id")
    rating = serializers.CharField(source="program.rating")
    intro_video_url = serializers.CharField(source="program.intro_video_url")
    image_url = serializers.CharField(source="program.image_url")
    expert = serializers.IntegerField(source="program.expert.id")

    title = serializers.CharField(source="program.title")
    slug = serializers.CharField(source="program.slug")
    price = serializers.DecimalField(source="program.price", max_digits=20, decimal_places=2, )
    duration_in_weeks = serializers.IntegerField(source="program.duration_in_weeks")
    start_date = serializers.DateField(source="batch_start_date")
    is_subscribed = serializers.SerializerMethodField()
    speciality = serializers.CharField(source="program.speciality")
    status = serializers.CharField(source="program.status")
    category = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = ProgramBatch
        fields = (
            "start_date", "batch_end_date", "offer_price", "capacity", "additional_days", "meet_link",
            "additional_start_date",

            "upcoming_session_id", "upcoming_session_start_date", "upcoming_session_start_time", "category",
            "is_favorite",
            "image_url", "batch_id", "id", "rating", "intro_video_url", "expert", "title", "slug", "price",
            "session_count", "duration_in_weeks", "is_subscribed", "speciality", "status")

    def get_upcoming_session_id(self, obj):
        batch_id = obj.id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id,
                                                                  session_date__gte=datetime.today().strftime(
                                                                      '%Y-%m-%d'))
        if programBatchSessions.exists():
            return programBatchSessions.order_by('session_date').first().id
        else:
            return None

    def get_upcoming_session_start_date(self, obj):
        batch_id = obj.id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id,
                                                                  session_date__gte=datetime.today().strftime(
                                                                      '%Y-%m-%d'))
        if programBatchSessions.exists():
            return programBatchSessions.order_by('session_date').first().session_date
        else:
            return None

    def get_upcoming_session_start_time(self, obj):
        batch_id = obj.id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id,
                                                                  session_date__gte=datetime.today().strftime(
                                                                      '%Y-%m-%d'))
        if programBatchSessions.exists():
            return programBatchSessions.order_by('session_date').first().start_time
        else:
            return None

    def get_session_count(self, obj):
        batch_id = obj.id

        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=batch_id)
        if programBatchSessions.exists():
            return programBatchSessions.count()
        else:
            return 0

    def get_is_subscribed(self, obj):
        is_subscribed = 'inactive'
        if ((hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and
             isinstance(self.context.get('user_id'), int)) and (
                ProgramBatchUser.objects.filter(user__id=self.context.get('user_id'),
                                                programBatch=obj.id).exists())):
            print('obj', )
            batch_id = obj.id
            data = ProgramBatchUser.objects.filter(user__id=self.context.get('user_id'),
                                                   programBatch__id=batch_id).values('status')
            print('data===', data)
            if len(data) > 0:
                if data[0]['status'] == "active":
                    is_subscribed = "active"
                    if data[0]['status'] == "payment_under_review":
                        self.is_subscribed = "payment_under_review"
        print('sub:', is_subscribed)
        return is_subscribed

    def get_category(self, obj):
        return list(ProgramCategory.objects.filter(program_id=obj.program.id).values_list('category__name', flat=True))

    def get_is_favorite(self, obj):
        is_favorite = False
        if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                self.context.get('user_id'), int):
            is_favorite = FavoriteProgram.objects.filter(program_id=obj.program.id,
                                                         user_id=self.context.get('user_id')).exists()
        return is_favorite


class UserProgramListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='program.id')
    title = serializers.CharField(source='program.title')
    slug = serializers.CharField(source='program.slug')
    rating = serializers.CharField(source='program.rating')
    intro_video_url = serializers.CharField(source='program.intro_video_url')
    image_url = serializers.CharField(source='program.image_url')
    expert = serializers.CharField(source='program.expert_id')
    auther = serializers.CharField(source='program.auther_id')
    html_description = serializers.CharField(source='program.html_description')
    price = serializers.DecimalField(source='program.price', max_digits=10, decimal_places=2)
    duration_in_weeks = serializers.IntegerField(source='program.duration_in_weeks')
    category = serializers.SerializerMethodField()
    batch_id = serializers.IntegerField(source='id')
    is_favorite = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    start_date = serializers.DateField(source='batch_start_date')
    session_count = serializers.SerializerMethodField()

    class Meta:
        model = ProgramBatch
        fields = (
            "id", "title", "slug", "rating", "intro_video_url", "image_url", "expert", "auther", "html_description",
            "batch_id", "offer_price",
            "price", "session_count", "duration_in_weeks", "start_date", "batch_end_date", "is_favorite",
            "is_subscribed",
            'category', 'capacity', 'additional_days')

    def get_category(self, obj):
        return list(ProgramCategory.objects.filter(program_id=obj.program_id).values_list('category__name', flat=True))

    def get_is_favorite(self, obj):
        is_favorite = False
        if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                self.context.get('user_id'), int):
            is_favorite = FavoriteProgram.objects.filter(program_id=obj.id,
                                                         user_id=self.context.get('user_id')).exists()
        return is_favorite

    def get_is_subscribed(self, obj):
        is_subscribed = 'inactive'
        if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                self.context.get('user_id'), int):
            if ProgramBatchUser.objects.filter(programBatch_id=obj.id, user_id=self.context.get('user_id')).exists():
                data = ProgramBatchUser.objects.filter(programBatch_id=obj.id,
                                                       user_id=self.context.get('user_id')).values('status')
                if data[0]['status'] == "active":
                    is_subscribed = "active"
                if data[0]['status'] == "payment_under_review":
                    self.is_subscribed = "payment_under_review"
        return is_subscribed

    def get_session_count(self, obj):
        programBatchSessions = ProgramBatchSession.objects.filter(programBatch_id=obj.id)
        if programBatchSessions.exists():
            return programBatchSessions.count()
        else:
            return 0


# class ProgramVideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Videos
#         fields = "__all__"


class ProgramReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'title', 'description', 'rating', 'program', 'user']


class ProgramFrequentlyAskedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestion
        fields = "__all__"


class ProgramBatchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramBatchUser
        fields = "__all__"


class FavoriteProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProgram
        fields = "__all__"


class ProgramBatchSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramBatchSession
        fields = "__all__"


class ProgramBatchSessionAccessedResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramBatchSessionResource
        fields = ("title", "description", "doc_type", "doc_url")


class ProgramBatchSessionNonAccessedResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramBatchSessionResource
        fields = ("title", "description", "doc_type")


class GlobalSearchProgramSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = UserProgramList
        fields = ("id", "title", 'rating', 'price', 'offer_price', 'batch_id', 'image_url', 'category')

    def get_category(self, obj):
        return list(ProgramCategory.objects.filter(program_id=obj.id).values_list('category__name', flat=True))


class ProgramTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramTask
        fields = ("id", "title", "desc", "task_time")


class AddActionTaskUserProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionTaskUserProgram
        fields = "__all__"


class ActionTaskUserProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionTaskUserProgram
        fields = ("id", "status", "task_id", "created_at")


class LevelTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTracker
        fields = "__all__"


class ProgramLevelTrackerSerializer(serializers.ModelSerializer):
    level_tracker = LevelTrackerSerializer(many=True, read_only=True)

    class Meta:
        model = ProgramLevelTracker
        fields = "__all__"


class ProgramLevelValueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramLevelValueType
        fields = ("value", "program_level", "value_type")


class ProgramSymptomTrackerValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramSymptomTrackerValue
        fields = ("program_symptom_tracker_value_date", "symptom", "value")


class ProgramLevelValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramLevelValue
        fields = "__all__"


class ProgramLevelValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramLevelValue
        fields = "__all__"


class ProgramSymptomTrackerValueDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramSymptomTrackerValueDate
        fields = "__all__"


class ProgramLevelValueSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ProgramLevelValue
        fields = "__all__"


class OverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Overview
        fields = "__all__"


class ProgramCategoryWiseSerializer(serializers.ModelSerializer):
    expert_name = serializers.SerializerMethodField('get_expert_name')
    expert_pic = serializers.SerializerMethodField('get_expert_pic')
    professional_title = serializers.SerializerMethodField('get_professional_title')

    class Meta:
        model = Program
        fields = (
            'id', 'title', 'professional_title', 'image_url', 'expert_name', 'expert_pic', 'category', 'speciality')

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


class UpcomingProgramSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField('get_start_date')
    expert_name = serializers.SerializerMethodField('get_expert_name')

    class Meta:
        model = Program
        fields = ['id', 'title', 'image_url', 'thumbnail_image', 'start_date', 'expert_name']

    def get_start_date(self, program):
        start_date = program.start_date.strftime('%d %b %Y')
        return start_date

    def get_expert_name(self, program):
        name = ""
        if program.expert.first_name:
            name += program.expert.first_name + " "
        if program.expert.last_name:
            name += program.expert.last_name
        return name


class ExpertAllProgramsSerializer(serializers.ModelSerializer):
    batch_id = serializers.SerializerMethodField('get_batch_id')
    program_id = serializers.SerializerMethodField('get_program_id')
    program_title = serializers.SerializerMethodField('get_program_title')
    image_url = serializers.SerializerMethodField('get_image_url')
    html_description = serializers.SerializerMethodField('get_html_description')
    batch_start_date = serializers.SerializerMethodField('get_start_date')
    program_status = serializers.SerializerMethodField('get_program_status')
    participants = serializers.SerializerMethodField('get_participants')

    class Meta:
        model = ProgramBatch
        fields = ['batch_id', 'program_id', 'program_title', 'image_url', 'html_description', 'batch_start_date',
                  'program_status', 'participants']

    def get_batch_id(self, obj):
        return obj.id

    def get_program_id(self, obj):
        return obj.program.id

    def get_program_title(self, obj):
        if obj.program.title and obj.title:
            title = obj.program.title + "|" + obj.title
            return title
        elif obj.program.title and obj.title is None:
            title = obj.program.title
            return title
        elif obj.program.title is None and obj.title:
            title = obj.title
            return title
        return ""

    def get_image_url(self, obj):
        return obj.program.image_url

    def get_html_description(self, obj):
        return obj.program.html_description

    def get_start_date(self, obj):
        start_date = obj.batch_start_date.strftime('%d %b %Y')
        return start_date

    def get_program_status(self, obj):
        today = datetime.today()
        status = ""
        if obj.batch_end_date:
            end_date = obj.batch_end_date
            if today.date() > end_date:
                status = "Completed"
            elif today.date() == end_date and obj.start_time <= today.time() <= obj.end_time:
                status = "Program is Live"
            elif today.date() < end_date and today.date() < obj.batch_start_date:
                delta = obj.batch_start_date - today.date()
                status = "Starts in " + str(delta.days) + " days"
            elif obj.batch_start_date <= today.date() <= end_date:
                status = "Program is Running"
        return status

    def get_participants(self, obj):
        today = datetime.today()
        participants = ""
        if obj.batch_end_date:
            end_date = obj.batch_end_date
            if today.date() == end_date and obj.start_time <= today.time() <= obj.end_time:
                total_user = ProgramBatchUser.objects.filter(programBatch_id=obj.id).count()
                participants = str(total_user) + " Participants"
        return participants


class UpcomingSessionSerializer(serializers.ModelSerializer):
    batch_id = serializers.SerializerMethodField('get_batch_id')
    program_id = serializers.SerializerMethodField('get_program_id')
    program_title = serializers.SerializerMethodField('get_program_title')
    image_url = serializers.SerializerMethodField('get_image_url')
    html_description = serializers.SerializerMethodField('get_html_description')
    session_date = serializers.SerializerMethodField('get_session_date')
    session_title = serializers.SerializerMethodField('get_session_title')

    class Meta:
        model = ProgramBatchSession
        fields = ['batch_id', 'program_id', 'program_title', 'session_title', 'image_url', 'html_description',
                  'session_date', 'sequence_num']

    def get_session_title(self, obj):
        return obj.title

    def get_batch_id(self, obj):
        return obj.programBatch.id

    def get_program_id(self, obj):
        return obj.programBatch.program.id

    def get_program_title(self, obj):
        title = obj.programBatch.program.title + "|" + obj.programBatch.title
        return title

    def get_image_url(self, obj):
        return obj.programBatch.program.image_url

    def get_html_description(self, obj):
        return obj.programBatch.program.html_description

    def get_session_date(self, obj):
        today = datetime.today()
        delta = obj.session_date - today.date()
        status = "Starts in " + str(delta.days) + " days"
        return status


class ProgramBatchSessionDetailsSerializer(serializers.ModelSerializer):
    session_id = serializers.SerializerMethodField('get_session_id')
    resources = serializers.SerializerMethodField('get_resources')
    session_date = serializers.DateField(format='%d/%m/%Y')

    class Meta:
        model = ProgramBatchSession
        fields = ['session_id', 'title', 'description', 'sequence_num', 'session_date', 'start_time', 'end_time',
                  'resources']

    def get_session_id(self, obj):
        return obj.id

    def get_resources(self, obj):
        resources = ProgramBatchSessionResource.objects.filter(programBatchSession=obj)
        resources = ProgramBatchSessionAccessedResourceSerializer(resources, many=True)
        return resources.data


class ProgramDetailsSerializer(serializers.ModelSerializer):
    expert_name = serializers.SerializerMethodField('get_expert_name')
    offer_price = serializers.SerializerMethodField('get_offer_price')
    program_status = serializers.SerializerMethodField('get_program_status')
    participants = serializers.SerializerMethodField('get_participants')
    participants_name = serializers.SerializerMethodField('get_participants_name')
    total_review = serializers.SerializerMethodField('get_total_review')
    total_rating = serializers.SerializerMethodField('get_total_rating')

    class Meta:
        model = Program
        fields = ['id', 'title', 'slug', 'rating', 'intro_video_url', 'image_url', 'html_description', 'price',
                  'offer_price',
                  'session_count', 'duration_in_weeks', 'start_date', 'speciality', 'expert_id', 'expert_name',
                  'program_status', 'participants', 'participants_name', 'total_review', 'total_rating']

    def get_expert_name(self, obj):
        name = ""
        if obj.expert.first_name:
            name += obj.expert.first_name + " "
        if obj.expert.last_name:
            name += obj.expert.last_name + " "
        return name

    def get_offer_price(self, obj):
        price = str(obj.get_current_batch_offer_price())

        if not obj.get_current_batch_id():
            if hasattr(self, 'context') and 'user_id' in self.context and self.context.get('user_id') and isinstance(
                    self.context.get('user_id'), int):
                if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                   programBatch__program_id=obj.id).exists():
                    if ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                       programBatch__program_id=obj.id).first().programBatch.offer_price:
                        price = str(ProgramBatchUser.objects.filter(user_id=self.context.get('user_id'),
                                                                    programBatch__program_id=obj.id).first().programBatch.offer_price)

        return price

    def get_program_status(self, obj):
        obj = self.context.get('batch')
        today = datetime.today()
        status = ""
        if obj.batch_end_date:
            end_date = obj.batch_end_date
            if today.date() > end_date:
                status = "Completed"
            elif today.date() == end_date and obj.start_time <= today.time() <= obj.end_time:
                status = "Program is Live"
            elif today.date() < end_date and today.date() < obj.batch_start_date:
                delta = obj.batch_start_date - today.date()
                status = "Starts in " + str(delta.days) + " days"
            elif obj.batch_start_date <= today.date() <= end_date:
                status = "Program is Running"
        return status

    def get_participants(self, obj):
        obj = self.context.get('batch')
        total_user = ProgramBatchUser.objects.filter(programBatch_id=obj.id).count()
        return total_user

    def get_participants_name(self, obj):
        obj = self.context.get('batch')
        name = []
        user_list = ProgramBatchUser.objects.filter(programBatch_id=obj.id).values_list('user', flat=True)[:3]
        name = User.objects.filter(id__in=user_list).values('first_name')
        return name

    def get_total_review(self, obj):
        count = Review.objects.filter(program=obj, status='approved').count()
        return count

    def get_total_rating(self, obj):
        total = Review.objects.filter(program=obj, status='approved').aggregate(total=Sum('rating'))['total']
        return total


class ExpertDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_expert_name')

    class Meta:
        model = User
        fields = ['id', 'name', 'professional_title', 'profile_picture']

    def get_expert_name(self, user):
        name = ""
        if user.first_name:
            name += user.first_name + " "
        if user.last_name:
            name += user.last_name
        return name


class ProgramListSerializer(serializers.ModelSerializer):
    program_id = serializers.IntegerField(source='program.id')
    batch_id = serializers.IntegerField(source='id')
    title = serializers.CharField(source='program.title')
    is_subscribed = serializers.SerializerMethodField()
    speciality = serializers.CharField(source="program.speciality")
    category = serializers.SerializerMethodField('get_category')
    is_favorite = serializers.SerializerMethodField()
    image_url = serializers.CharField(source="program.image_url")
    expert = serializers.SerializerMethodField('get_expert')

    # expert_id = serializers.IntegerField(source="program.expert.id")
    # expert_name = serializers.CharField(source='program.expert.first_name')
    # professional_title = serializers.CharField(source='program.expert.professional_title')
    # expert_pic = serializers.SerializerMethodField('get_expert_pic')

    class Meta:
        model = ProgramBatch
        fields = ['program_id', 'batch_id', 'title', 'is_subscribed', 'speciality', 'category', 'is_favorite',
                  'image_url', 'expert']

    def get_is_subscribed(self, obj):
        is_subscribed = 'inactive'
        user = self.context.get('user')
        if ProgramBatchUser.objects.filter(user__id=user.id, programBatch__id=obj.id).exists():
            data = ProgramBatchUser.objects.get(user__id=user.id, programBatch__id=obj.id)
            is_subscribed = data.status
        return is_subscribed

    def get_category(self, obj):
        ids = ProgramCategory.objects.filter(program_id=obj.program.id).values_list('category')
        category = Category.objects.filter(id__in=ids)
        serializers = CustomCategorySerializer(category, many=True)
        return serializers.data

    def get_is_favorite(self, obj):
        user = self.context.get('user')
        is_favorite = FavoriteProgram.objects.filter(program_id=obj.program.id,
                                                     user_id=user.id).exists()
        return is_favorite

    def get_expert_pic(self, obj):
        if obj.program.expert.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.program.expert.profile_picture))
            return profile_picture
        return ""

    def get_expert(self, obj):
        # data = User.objects.filter(id=obj.program.expert.id)
        serializers = ExpertDetailSerializer(obj.program.expert, many=False)
        return serializers.data


class ProgramReviewDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    name = serializers.SerializerMethodField('get_user_name')
    profile_picture = serializers.SerializerMethodField('get_user_pic')
    like_count = serializers.SerializerMethodField('get_like_count')

    class Meta:
        model = Review
        fields = ['id', 'title', 'description', 'rating', 'program', 'user_id', 'name', 'profile_picture','like_count']

    def get_user_name(self, obj):
        name = ""
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name
        return name

    def get_user_pic(self, obj):
        if obj.user.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.user.profile_picture))
            return profile_picture
        return ""

    def get_like_count(self,obj):
        return obj.like.count()