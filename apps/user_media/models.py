from django.db import models

from apps.common_utils.Aws import Aws, AwsFilePath
from apps.user.models import User

class Media(models.Model):
    
    file_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    alt_text = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    caption = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    description = models.TextField(
        "mdeia description",
        null=True,
        blank=True,
    )
    media_file = models.FileField(
        "temporary field for getting file from admin panel",
        null=True,
        blank=True,
    )
    file_url = models.CharField(
        "actual doc file url",
        max_length=150,
        null=True,
        blank=True,
    )
    created_timestamp = models.DateTimeField(
        'session creation date',
        auto_now_add=True,
    )
    last_modified_timestamp = models.DateTimeField(
        auto_now=True,
    )
    created_by = models.ForeignKey(
        User,
        related_name="media_uploaded_by_user",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    last_updated_by = models.ForeignKey(
        User,
        related_name="media_last_updated_by_user",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):         
        super(Media, self).save(*args, **kwargs)

        if self.media_file:
            aws = Aws()
            fileUploadPath = AwsFilePath.userMediaFilePath(
                user_id = self.last_updated_by_id,
                resource_file_name = self.media_file.name,
            )
            self.file_url = aws.upload_file(self.media_file, fileUploadPath)
            self.media_file = None
            super(Media, self).save(force_insert=False, force_update=True, using='default', update_fields=None)


class StaticResources(models.Model):
    
    title = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    slug = models.CharField(
        unique=True,
        max_length=200,
        null=True,
        blank=True,
    )
    resource_file_url = models.CharField(
        "actual doc file url",
        max_length=150,
        null=True,
        blank=True,
    )
    resource_file = models.FileField(
        "field to upload file",
        null=True,
        blank=True,
    )
    keywords = models.TextField(
        null=True,
        blank=True,
    )
    html_body = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        'resource aaded at',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "resource updaated at",
        auto_now=True,
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):         
        super(StaticResources, self).save(*args, **kwargs)

        if self.resource_file:
            aws = Aws()
            fileUploadPath = AwsFilePath.staticResourcesFilePath(
                resource_id = self.id,
                resource_file_name = self.resource_file.name,
            )
            self.resource_file_url = aws.upload_file(self.resource_file, fileUploadPath)
            self.resource_file = None
            super(StaticResources, self).save(force_insert=False, force_update=True, using='default', update_fields=None)

