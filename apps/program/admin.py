from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet, ModelChoiceField
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)
from admin_numeric_filter.admin import (
    NumericFilterModelAdmin, SingleNumericFilter, RangeNumericFilter, \
    SliderNumericFilter
)
from rangefilter.filter import (
    DateRangeFilter, DateTimeRangeFilter
)

from apps.common_utils import constants
from apps.user.models import Category
from .models import (
    Program,
    Overview,
    Review,
    FrequentlyAskedQuestion,
    ProgramBatchUser,
    ProgramCategory,
    ProgramSession,
    ProgramSessionResource,
    ProgramBatch,
    ProgramBatchSession,
    ProgramBatchSessionResource,
    UserPaymentDetail,
    Discount,
    DiscountStatistics, ProgramTask, LevelTracker, LevelTrackerTag, LevelTrackerValueType, ProgramLevelTracker,
    SymptomTracker, ProgramSymptomTracker, ReviewFiles
)

from apps.user.models import User


class ScheduledDaysOfWeekForm(forms.ModelForm):
    scheduled_days_of_week = forms.MultipleChoiceField(
        widget=forms.SelectMultiple,
        choices=constants.WEEK_DAYS,
        initial="Monday",
        help_text="""
    This is Only Applicable if <b>scheduling_strategy</b> is selected <b>WEEKLY</b> <br>
    <b>Multi Selection Command : ctrl + click </b>
    """,
    )


'''
allowing user must select atleast one program category
'''


class ProgramCategoryInline(BaseInlineFormSet):
    def clean(self) -> None:
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass

        if count < 1:
            raise ValidationError('You must have at least one program category')


class CategoryInline(admin.TabularInline):
    model = ProgramCategory
    extra = 1
    formset = ProgramCategoryInline


class ProgramSessionResourceInline(admin.TabularInline):
    model = ProgramSessionResource
    extra = 0
    show_change_link = True


class ProgramSessionInline(admin.TabularInline):
    model = ProgramSession
    extra = 0
    show_change_link = True


class ProgramBatchSessionResourceInline(admin.TabularInline):
    model = ProgramBatchSessionResource
    extra = 0
    show_change_link = True


class ProgramBatchSessionInline(admin.TabularInline):
    model = ProgramBatchSession
    extra = 0
    show_change_link = True


class ProgramBatchInline(admin.TabularInline):
    model = ProgramBatch
    readonly_fields = ['batch_end_date', 'additional_start_date']
    form = ScheduledDaysOfWeekForm
    extra = 0
    show_change_link = True


class ProgramAdminForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ("title", "slug", "rating", "intro_video_url", "image_url", "thumbnail_image",
                  "expert", "html_description", "price", "session_count", "speciality",
                  "duration_in_weeks", "start_date", "status", "chat_group_key", "category")

    def clean_thumbnail_image(self):
        if not self.cleaned_data["thumbnail_image"] and not self.cleaned_data["image_url"]:
            raise forms.ValidationError("This Field Required")
        return self.cleaned_data["thumbnail_image"]


class ProgramAdmin(admin.ModelAdmin):
    form = ProgramAdminForm
    search_fields = ('id', 'title', 'price', 'start_date', 'status')
    list_filter = [
        ('category', RelatedDropdownFilter),
        ('expert', RelatedDropdownFilter),
        ('auther', RelatedDropdownFilter),
        ('price', RangeNumericFilter),
        ('rating', RangeNumericFilter),
        'status'
    ]
    list_display = 'id', 'title', 'price', 'session_count', 'duration_in_weeks', 'start_date', 'status'
    exclude = ('chat_group_key',)
    inlines = [
        CategoryInline,
        ProgramSessionInline,
        ProgramBatchInline
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if (db_field.name == 'expert'):
            kwargs['queryset'] = User.objects.filter(user_type='expert').order_by('first_name')
        if (db_field.name == 'auther'):
            kwargs['queryset'] = User.objects.filter(user_type='expert').order_by('first_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Program, ProgramAdmin)


class ProgramSessionAdmin(admin.ModelAdmin):
    inlines = [
        ProgramSessionResourceInline,
    ]
    search_fields = ("id", 'program__title', "title")
    list_filter = [
        ('program', RelatedDropdownFilter),
        ('created_at', DateTimeRangeFilter),
        ('last_updated_at', DateTimeRangeFilter),
        'session_type'
    ]
    list_display = 'id', 'program', 'title', 'sequence_num', 'duration', 'session_type', 'created_at', 'last_updated_at'


admin.site.register(ProgramSession, ProgramSessionAdmin)


class ProgramBatchAdmin(admin.ModelAdmin):
    form = ScheduledDaysOfWeekForm
    readonly_fields = ('batch_end_date', 'additional_start_date')
    inlines = [
        ProgramBatchSessionInline,
    ]

    search_fields = ("id", 'program__title', 'title', 'batch_start_date', 'batch_status')

    list_filter = [
        ('program', RelatedDropdownFilter),
        'scheduling_strategy',
        ('batch_start_date', DateRangeFilter),
        ('batch_end_date', DateRangeFilter),
        ('start_time', DateTimeRangeFilter),
        ('end_time', DateTimeRangeFilter),
        ('offer_price', RangeNumericFilter),
    ]

    list_display = ['id', 'program', 'title', 'start_time', 'end_time', 'batch_start_date', 'batch_end_date',
                    'scheduling_strategy', 'scheduled_days_of_week', 'scheduled_day_of_month', 'batch_status',
                    "offer_price", 'meet_link', 'created_at', 'last_updated_at']

    fields = ['program', "title", 'start_time', 'end_time', 'batch_start_date', 'batch_end_date', 'scheduling_strategy',
              'scheduled_days_of_week', 'scheduled_day_of_month', 'batch_status',
              "offer_price", 'meet_link', 'capacity', 'additional_days', 'additional_start_date']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('program',)
        return self.readonly_fields


admin.site.register(ProgramBatch, ProgramBatchAdmin)


class ProgramBatchSessionAdmin(admin.ModelAdmin):
    search_fields = ("id", 'programBatch__title', 'title')

    inlines = [
        ProgramBatchSessionResourceInline,
    ]
    list_filter = [
        ('programBatch', RelatedDropdownFilter),
        ('created_at', DateTimeRangeFilter),
        ('last_updated_at', DateTimeRangeFilter),
        'session_type'
    ]
    list_display = 'id', 'programBatch', 'title', 'sequence_num', 'duration', 'session_type', 'session_date', 'start_time', 'end_time', 'actual_start_datetime'


admin.site.register(ProgramBatchSession, ProgramBatchSessionAdmin)


class ProgramSessionResourceAdmin(admin.ModelAdmin):
    list_display = "id", "programSession"


admin.site.register(ProgramSessionResource, ProgramSessionResourceAdmin)


class OverviewAdmin(admin.ModelAdmin):
    search_fields = ('title', 'header_image_link', 'description', 'program__title')
    list_filter = [
        ('program', RelatedDropdownFilter),
    ]
    list_display = 'title', 'header_image_link', 'description', 'program'


admin.site.register(Overview, OverviewAdmin)


class ReviewAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description', 'program__title')
    list_filter = [
        ('program', RelatedDropdownFilter),
    ]
    list_display ='id', 'title', 'description', 'program','status'


admin.site.register(Review, ReviewAdmin)


# class VideosAdmin(admin.ModelAdmin):
#     search_fields = ('youtube_video_link', 'program__title')
#     list_filter = [
#         ('program', RelatedDropdownFilter),
#     ]
#     list_display = "id", 'youtube_video_link', 'program'
#
#
# admin.site.register(Videos, VideosAdmin)


class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
    search_fields = ('question', 'answer', 'program__title')
    list_filter = [
        ('program', RelatedDropdownFilter),
    ]
    list_display = 'question', 'answer', 'program'


admin.site.register(FrequentlyAskedQuestion, FrequentlyAskedQuestionAdmin)


class ProgramBatchUserAdmin(admin.ModelAdmin):
    search_fields = ('programBatch__title', 'user__first_name', 'user__last_name', 'status')
    list_filter = [
        ('programBatch', RelatedDropdownFilter),
        ('user', RelatedDropdownFilter),
    ]
    list_display = 'programBatch', 'user', 'status', 'subscription_date'


admin.site.register(ProgramBatchUser, ProgramBatchUserAdmin)


class UserPaymentDetailAdmin(admin.ModelAdmin):
    search_fields = ("id", "first_name", "last_name", "email_id")
    readonly_fields = ['screen_short']


admin.site.register(UserPaymentDetail, UserPaymentDetailAdmin)


class DiscountAdmin(admin.ModelAdmin):
    search_fields = ("id", "code")
    list_display = ("id", "code", "valid_from_timestamp", "valid_till_stamp", "discount_type", "status")
    list_filter = ("code", "valid_from_timestamp", "valid_till_stamp", "discount_type", "status")


admin.site.register(Discount, DiscountAdmin)


class DiscountStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "id", "discount_applied_timestamp", "amount", "discount_amount", "amount_after_discount", "program", "user",
        "discount", "discount_code", "status")
    list_filter = ("discount_applied_timestamp", "amount", "discount_amount", "amount_after_discount", "status")


admin.site.register(DiscountStatistics, DiscountStatisticsAdmin)


class ProgramTaskAdmin(admin.ModelAdmin):
    search_fields = ("id", 'title', 'desc')

    list_filter = [
        ('program', RelatedDropdownFilter),
        'title'
    ]

    list_display = ['id', "program", "title", 'desc', 'task_time']

    fields = ['program', "title", 'desc', 'task_time']


admin.site.register(ProgramTask, ProgramTaskAdmin)


class LevelTrackerTagInline(admin.TabularInline):
    model = LevelTrackerTag
    extra = 0
    show_change_link = True


class LevelTrackerValueTypeInline(admin.TabularInline):
    model = LevelTrackerValueType
    extra = 0
    show_change_link = True


class LevelTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "icon_url")
    list_filter = ("id", "title")

    inlines = [
        LevelTrackerTagInline,
        LevelTrackerValueTypeInline
    ]


admin.site.register(LevelTracker, LevelTrackerAdmin)


class ProgramLevelTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "program", "level_tracker")
    list_filter = ("id", "program", "level_tracker")


admin.site.register(ProgramLevelTracker, ProgramLevelTrackerAdmin)


class SymptomTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_filter = ("id", "title")


admin.site.register(SymptomTracker, SymptomTrackerAdmin)


class ProgramSymptomTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "program", "symptom_tracker")
    list_filter = ("id", "program", "symptom_tracker")


admin.site.register(ProgramSymptomTracker, ProgramSymptomTrackerAdmin)


class ReviewFilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'files')


admin.site.register(ReviewFiles,ReviewFilesAdmin)
