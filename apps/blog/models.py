import re
from django.db import models
from apps.user.models import User, Category
from apps.common_utils import constants
from apps.common_utils.Aws import Aws, AwsFilePath
from django.core.validators import FileExtensionValidator


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
        return "(" + str(self.id) + ") " + self.tag_name


class Blog(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=False
    )
    summary = models.TextField(
        null=True,
        blank=False
    )
    feature_image_url = models.CharField(
        "Actual Feature Image Url",
        max_length=500,
        null=True,
        blank=True
    )
    banner_image_url = models.CharField(
        "Actual Banner Image Url",
        max_length=500,
        null=True,
        blank=True
    )
    article_body = models.TextField()
    expert = models.ForeignKey(
        User,
        related_name='blog_expert',
        null=True,
        on_delete=models.CASCADE
    )
    slug = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=False
    )
    categories = models.ManyToManyField(
        Category,
        related_name='blog_caegories',
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='blog_tags',
        blank=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    approved_by = models.ForeignKey(
        User,
        related_name='blog_approver',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        choices=constants.BLOG_STATUS,
        max_length=20,
        default='draft'
    )
    rejection_message = models.CharField(
        "reason for article rejection",
        max_length=200,
        null=True,
        blank=True,
    )
    blog_state = models.ManyToManyField(
        User,
        through='BlogStates',
        related_name='blog_state',
    )

    feature_image = models.ImageField(upload_to='blog', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'], message="Only jpeg,jpg and png allowed")])

    favourite = models.ManyToManyField(User, related_name='favourite_blog', blank=True, null=True)

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
            super(Blog, self).save(*args, **kwargs)
        else:
            super(Blog, self).save(force_insert=False, force_update=True, using='default', update_fields=None)


class BlogView(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )


class BlogLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('blog', 'user',)


class BlogComment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE
    )
    comment = models.TextField(
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )


class BlogShare(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    where = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


class BlogStates(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    is_view = models.BooleanField(
        'blog view or not',
        default=False
    )
    viewed_time = models.DateTimeField(
        auto_now=True
    )
    is_like = models.BooleanField(
        'blog liked or not',
        default=False
    )
    liked_time = models.DateTimeField(
        'liked time',
        auto_now=True
    )
    is_shared = models.BooleanField(
        'shared or not',
        default=False
    )
    shared_time = models.DateTimeField(
        'sahred time',
        auto_now=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        max_length=20,
        default='active'
    )
