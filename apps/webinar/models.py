from django.db import models
from apps.user.models import User, Category
from apps.common_utils import constants
from apps.common_utils.Aws import Aws, AwsFilePath
from django.utils.text import slugify
import time


# Create your models here.

class Webinar(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    )
    title = models.CharField(
        max_length=200,
        null=True,
        blank=False
    )
    slug = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    meta_keywords = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    video_link = models.CharField(
        max_length=200,
        blank=False,
        null=True
    )
    thumbnail_image = models.FileField(
        "temporary field for getting file from admin panel",
        null=True,
        blank=True,
    )
    thumbnail_url = models.CharField(
        "actual s3 file url",
        max_length=150,
        null=True,
        blank=True,
    )
    category = models.ManyToManyField(
        Category,
        through='WebinarCategory',
        related_name='webinar_categories',
    )

    description = models.TextField(null=True, blank=False, help_text="Min. 150 character")
    webinar_date = models.DateField(blank=False, null=True)
    start_time = models.TimeField(blank=False, null=True)
    end_time = models.TimeField(blank=False, null=True)
    expert = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
    whatsapp_link = models.CharField(max_length=200, blank=True, null=True)
    blue_bird_email_template_id = models.CharField(max_length=5, blank=False, null=True, default='108')
    displayOrder = models.IntegerField(default=0)
    status = models.CharField(choices=STATUS, max_length=100, blank=False, null=False, default='Inactive')
    createdAt = models.DateField(
        'created date',
        auto_now_add=True,
    )
    favourite = models.ManyToManyField(User, related_name="favourite_webinar", blank=True, null=True)

    def save(self, *args, **kwargs):

        super(Webinar, self).save(*args, **kwargs)
        if self.slug is None:
            self.slug = slugify(self.title) + "-" + str(int(time.time()))

        if self.thumbnail_image:
            aws = Aws()
            fileUploadPath = AwsFilePath.webinarMediaFilePath(
                slug=self.slug,
                resource_file_name=self.thumbnail_image.name,
            )
            self.thumbnail_url = aws.upload_file(self.thumbnail_image, fileUploadPath)
            self.thumbnail_image = None
            super(Webinar, self).save(force_insert=False, force_update=True, using='default', update_fields=None)

    class Meta:
        ordering = ['-webinar_date']

    def __str__(self):
        return self.title


class WebinarCategory(models.Model):
    webinar = models.ForeignKey(
        Webinar,
        related_name='webinar_for_category',
        on_delete=models.CASCADE,
        blank=False
    )
    category = models.ForeignKey(
        Category,
        related_name='webinar_category',
        on_delete=models.CASCADE,
        blank=False
    )

    class Meta:
        unique_together = (("webinar", "category"),)

    def __str__(self) -> str:
        return f'{self.category.name}'


class WebinarSubscriber(models.Model):
    STATUS = (
        ('Attended', 'Attended'),
        ('Not Attended', 'Not Attended')
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    whatsapp_mobile_no = models.CharField(max_length=100, blank=False, null=False)
    subscriptionDatetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('whatsapp_mobile_no', 'webinar')

    def __str__(self):
        return self.name


class Section(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    )
    title = models.CharField(max_length=100, blank=False, null=False)
    content = models.TextField(default="", blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(User, related_name="created_users", on_delete=models.CASCADE, blank=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True)
    updatedBy = models.ForeignKey(User, related_name="updated_users", on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=100, blank=True, null=True, default='Active')

    def __str__(self):
        return self.title


class WebinarSection(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    )
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True, null=True)
    overiddenContent = models.TextField(blank=True, null=True)
    displayOrder = models.IntegerField(default=0)
    status = models.CharField(choices=STATUS, max_length=10, default='Inactive', blank=False, null=False)

    class Meta:
        ordering = ['displayOrder']

    def __str__(self):
        return f'{self.webinar.title} - {self.section.title}'
