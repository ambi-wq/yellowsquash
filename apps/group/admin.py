from django import forms
from django.contrib import admin
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
from apps.group.models import GroupCategory, Group, GroupInvited, GroupRequested, GroupMembers, GroupPost

from apps.user.models import User


class GroupCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_title")
    list_filter = ("id", "category_title")


admin.site.register(GroupCategory, GroupCategoryAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "privacy", "author")
    list_filter = ("id", "name", "privacy", "author")


admin.site.register(Group, GroupAdmin)


class GroupInvitedAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "member", "invited_by", "status", "status_modified_on")
    list_filter = ("id",  "group", "member", "invited_by", "status")


admin.site.register(GroupInvited, GroupInvitedAdmin)


class GroupRequestedAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "member", "status", "status_modified_on")
    list_filter = ("id",  "group", "member", "status")


admin.site.register(GroupRequested, GroupRequestedAdmin)


class GroupMembersAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "member", "added_on")
    list_filter = ("id",  "group", "member")


admin.site.register(GroupMembers, GroupMembersAdmin)


class GroupPostsAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "member", "added_on", "status", "status_changed_by", "status_modified_on")
    list_filter = ("id",  "group", "member")


admin.site.register(GroupPost, GroupPostsAdmin)
