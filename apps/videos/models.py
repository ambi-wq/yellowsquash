from django.db import models
from apps.common_utils import constants
from apps.user.models import User,Category
from django.core.validators import FileExtensionValidator

import re


# Create your models here.
class Tag(models.Model):
    tag_name = models.CharField(
        max_length=50,
        unique=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
        )
    status = models.CharField(
        choices=constants.TAG_STATUS,
        max_length=10,
        default='active'
    )

    def __str__(self):
        return "(" + str(self.id) + ") "  + self.tag_name


class Video(models.Model):
    title = models.CharField(max_length=100,unique=True,null=True,blank=False)
    category = models.ManyToManyField(Category,blank=True,related_name='video_category')
    tags = models.ManyToManyField(
        Tag,
        related_name='video_tags',
        blank=False,
    )
    expert = models.ForeignKey(
        User,
        related_name='video_expert',
        null=True,
        on_delete=models.CASCADE
    )
    slug = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=False
    )
    thumbnail = models.ImageField(upload_to='videos',null=True,blank=True,validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'],message="Only jpeg,jpg and png allowed")])
    upload_video = models.FileField(upload_to='videos',null=True,blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    approved_by = models.ForeignKey(
        User,
        related_name='video_approver',
        null=True,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        choices=constants.BLOG_STATUS,
        max_length=20,
        default='draft'
    )
    rejection_message = models.CharField(
        "reason for video rejection",
        max_length=200,
        null=True,
        blank=True,
    )

    favourite = models.ManyToManyField(User, related_name='favourite_video', blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        isCreateCall = self.pk is None

        # make slug out of title : if it is not in blog model object or don't have space in it
        if not self.slug:
            self.slug = self.title[0].lower() if type(self.title) == tuple else self.title.lower()

        self.slug = re.sub(r"[^a-zA-Z0-9]+", '-', self.slug)

        while ' ' in self.slug:
            self.slug = self.slug.replace(" ", "-")

        if isCreateCall:
            super(Video, self).save(*args, **kwargs)
        else:
            super(Video, self).save(force_insert=False, force_update=True, using='default', update_fields=None)
