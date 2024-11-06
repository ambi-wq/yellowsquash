from datetime import timedelta, date, datetime

from django.db import models

from urllib.request import urlopen
from tempfile import NamedTemporaryFile

from django.core import validators
from django.core.files import File
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField
from apps.tinode.tinode import Tinode
from apps.common_utils import constants
from apps.user.models import User, Category
from apps.common_utils.Aws import Aws, AwsFilePath
import json
import logging
from django.utils.html import format_html
from django.utils.text import slugify
import time

logger = logging.getLogger(__name__)


class GroupCategory(models.Model):
    category_title = models.CharField(
        max_length=200,
        blank=False,
        null=True
    )

    def __str__(self):
        return self.category_title

    class Meta:
        verbose_name = 'Group Category'


class Group(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        null=True
    )
    about = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )
    rules = models.TextField(
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        related_name='group_author',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    privacy = models.CharField(
        choices=constants.PRIVACY_CHOICES,
        default='public',
        max_length=60
    )
    cover_image = models.CharField(
        max_length=4000
    )
    post_mode = models.CharField(
        choices=constants.POST_MODE_CHOICES,
        default='admin',
        max_length=60
    )
    status = models.CharField(
        choices=constants.GROUP_APPROVAL_STATUS,
        default='approved',
        max_length=60
    )
    created_on = models.DateTimeField(
        default=datetime.now()
    )

    def __str__(self):
        # return f'{self.name} / {self.category} / {self.privacy}'
        return f'{self.name}  / {self.privacy}'


class GroupAdmin(models.Model):
    group = models.ForeignKey(
        Group,
        related_name='ggroup_invited_group_admin',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_invited_member_admin',
        null=True,
        on_delete=models.DO_NOTHING,
    )


class GroupCategoryMapping(models.Model):
    category = models.ForeignKey(
        GroupCategory,
        related_name='ggroup_group_category',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    group = models.ForeignKey(
        Group,
        related_name='ggroup_invited_group',
        null=True,
        on_delete=models.DO_NOTHING,
    )


class GroupInvited(models.Model):
    group = models.ForeignKey(
        Group,
        related_name='group_invited_group',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_invited_member',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    invited_by = models.ForeignKey(
        User,
        related_name='group_added_by',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    status = models.CharField(
        choices=constants.GROUP_APPROVAL_STATUS,
        default='pending',
        max_length=60
    )
    status_modified_on = models.DateTimeField(
        default=datetime.now
    )
    created_on = models.DateTimeField(
        default=datetime.now
    )

    class Meta:
        unique_together = ('group', 'member',)


class GroupRequested(models.Model):
    group = models.ForeignKey(
        Group,
        related_name='group_requested_group',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_requested_member',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    status = models.CharField(
        choices=constants.GROUP_APPROVAL_STATUS,
        default='pending',
        max_length=60
    )
    status_modified_by = models.ForeignKey(
        User,
        related_name='group_requested_modby',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    status_modified_on = models.DateTimeField(
        default=datetime.now
    )

    class Meta:
        unique_together = ('group', 'member',)


class GroupMembers(models.Model):
    group = models.ForeignKey(
        Group,
        related_name='group_group',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_member',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    added_on = models.DateTimeField(
        default=datetime.now
    )

    class Meta:
        unique_together = ('group', 'member',)


class GroupPost(models.Model):
    group = models.ForeignKey(
        Group,
        related_name='group_post_group',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_post_member',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    added_on = models.DateTimeField(
        default=datetime.now
    )
    status_changed_by = models.ForeignKey(
        User,
        related_name='group_post_approved_by',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    status = models.CharField(
        choices=constants.GROUP_APPROVAL_STATUS,
        default='approved',
        max_length=60
    )
    status_modified_on = models.DateTimeField(
        default=datetime.now
    )
    text = models.TextField()
    tags = models.CharField(
        max_length=200
    )


class GroupPostMedia(models.Model):
    post = models.ForeignKey(
        GroupPost,
        related_name='group_media_post_group',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    media = models.CharField(
        max_length=4000
    )


class GroupPostLike(models.Model):
    post = models.ForeignKey(
        GroupPost,
        related_name='group_post_like_post',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_post_like_member',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    added_on = models.DateTimeField(
        default=datetime.now
    )

    class Meta:
        unique_together = ('post', 'member',)


class GroupPostComment(models.Model):
    post = models.ForeignKey(
        GroupPost,
        related_name='group_post_comment_post',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    member = models.ForeignKey(
        User,
        related_name='group_post_comment_member',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    comment = models.CharField(
        max_length=8000
    )

    parent_comment = models.ForeignKey('self', null=True, on_delete=models.DO_NOTHING)

    added_on = models.DateTimeField(
        default=datetime.now
    )
