import base64, os
import datetime

from django.utils.html import mark_safe
from django.utils.html import format_html
from django.db import models

from django.core import validators
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import JSONField

from django.utils.translation import ugettext_lazy as _
from apps.common_utils import constants
from apps.common_utils.Aws import Aws, AwsFilePath


class UserManager(BaseUserManager):
    def create_user(self, username, first_name='', last_name='', password=None):
        if not username:
            raise ValueError("User must have an username")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(username)
        )
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name='', last_name='', password=None):
        try:
            if not username:
                raise ValueError("User must have an username")
            if not password:
                raise ValueError("User must have a password")

            user = self.model(
                email=self.normalize_email(username)
            )
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.set_password(password)
            user.is_superuser = True
            user.save(using=self._db)
            return user
        except BaseException as err:
            print(err)


class User(AbstractBaseUser, PermissionsMixin):
    """all users"""

    username = models.CharField(
        'username',
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$'
            ),
        ],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    mobile = models.CharField(
        max_length=100,
        null=True,
        blank=True,

    )
    title = models.CharField(
        choices=constants.TITLE_CHOICES,
        max_length=30,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        'first name',
        max_length=30,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        'last name',
        max_length=30,
        null=True,
        blank=True,
    )
    nick_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    user_type = models.CharField(
        choices=constants.TYPE_CHOICES,
        max_length=100,
        blank=True,
        default='customer',
    )
    # this field is duplicate of short_description so need to be remove
    biographic_info = models.TextField(
        null=True,
        blank=True,
    )
    user_img = models.TextField(
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    email = models.CharField(
        'email address',
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        validators=[
            validators.RegexValidator(
                r'^[а-яА-Яa-zA-Z0-9_.+-]+@[а-яА-Яa-zA-Z0-9-]+\.[а-яА-Яa-zA-Z0-9-.]+$',
                'Enter a valid email address.'
            ),
        ]
    )
    is_verified = models.BooleanField(
        'verification status',
        default=False,
        help_text='Designates whether the user is verified or not',
    )
    email_verified = models.BooleanField(
        'email verification status',
        default=False,
        help_text='Designates whether the user email is verified or not',
    )
    mobile_verified = models.BooleanField(
        'mobile verification status',
        default=False,
        help_text='Designates whether the user mobile is verified or not',
    )
    password = models.CharField(
        'user password',
        max_length=255,
        blank=True,
        default='',
    )
    expert_score = models.IntegerField(
        default=0,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        'date joined',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )
    short_description = models.TextField(
        null=True,
        blank=True,
    )

    """
    additional data fields for specified users
    """
    designation = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    qualification = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    experience = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )

    fb_link = models.CharField(
        "facebook profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    twitter_link = models.CharField(
        "twitter  profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    linked_link = models.CharField(
        "linkedin profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    google_link = models.CharField(
        "google profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    tinode_token = models.CharField(
        "token for chat and all",
        max_length=500,
        null=True,
        blank=True,
    )
    category = models.ManyToManyField(
        'Category',
        through='UserIntrestOrExpertise',
        related_name='user_intrests_or_experties',
    )

    professional_title = models.CharField(
        'professional_title',
        max_length=100,
        null=True,
        blank=True,
    )

    video_url = models.CharField(
        'about expert video url',
        max_length=100,
        null=True,
        blank=True,
    )
    is_profile_complete = models.BooleanField(
        default=False
    )
    profile_picture = models.ImageField(null=True, blank=True)
    # location = models.CharField(
    #     'location',
    #     max_length=150,
    #     null=True,
    #     blank=True,
    # )
    # language = models.CharField(
    #     'language',
    #     max_length=250,
    #     default='English',
    #     null=False,
    #     blank=False,
    # )
    # experties = models.CharField(
    #     max_length=500,
    #     null=True,
    #     blank=True,
    # )
    location = models.ForeignKey('Location', related_name='location', blank=True, null=True, on_delete=models.CASCADE)
    language = models.ManyToManyField('Languages', related_name='languages', blank=True, null=True)
    experties = models.ManyToManyField('Expertise', related_name='expertise', blank=True, null=True)
    timezone = models.ForeignKey('Timezone', related_name='timezone', blank=True, null=True, on_delete=models.CASCADE)
    age = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)

    @property
    def is_staff(self):
        ''' IS the user a member of staff? '''
        return (self.status and self.status == 'active')

    def get_user_fullname(self):
        name = ""
        if self.title:
            name += self.title + " "
        if self.first_name:
            name += self.first_name + " "
        if self.last_name:
            name += self.last_name + " "
        return name

    def __str__(self):
        name = ""
        if self.title:
            name += self.title + " "
        if self.first_name:
            name += self.first_name + " "
        if self.last_name:
            name += self.last_name + " "

        name += " (" + self.user_type + ")"
        return name

    '''
    def profile_picture(self):
        from django.utils.html import escape
        return format_html('<img src="%s" width="50px"/>' % (self.user_img))

    profile_picture.short_description = 'Profile Picture'
    profile_picture.allow_tags = True
    '''

    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        ordering = ['first_name']


class UserCourseNameSuggestions(models.Model):
    course_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True
    )


class UserEducationDetail(models.Model):

    def current_year():
        return datetime.date.today().year

    user = models.ForeignKey(
        User,
        related_name='certified_user',
        on_delete=models.CASCADE,
        null=False,
    )
    # course_name = models.CharField(
    #     "user course name",
    #     max_length=100,
    #     null=False,
    #     blank=False,
    # )

    institution_name = models.CharField(
        "user institution name",
        max_length=100,
        null=False,
        blank=False,
    )
    completion_year = models.CharField(
        "completion year",
        max_length=4,
        null=True,
        blank=True,
    )
    # completion_year = models.CharField(
    #     "completion year",
    #     choices=constants.YEAR_CHOICES,
    #     default=current_year(),
    #     max_length=10
    #
    # )
    description = models.TextField(null=True,
                                   blank=True)
    certificate_doc = models.FileField(
        null=True,
        blank=True
    )
    certificate_doc_url = models.CharField(
        "actual certificate url",
        max_length=200,
        null=True,
        blank=True
    )

    course_name = models.ForeignKey('DegreeCertification', related_name="DegreeCertification", blank=True, null=True,
                                    on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'course_name',)

    def DownloadDocument(self):
        return format_html('<a href="%s" target="_blank">%s</a>' % (self.certificate_doc_url, 'Download'))

    def save(self, *args, **kwargs):
        super(UserEducationDetail, self).save(*args, **kwargs)
        if self.certificate_doc:
            aws = Aws()
            fileUploadPath = AwsFilePath.userCertificateDocPath(
                user_id=self.user.id,
                course_name=self.course_name,
                resource_file_name=self.certificate_doc.name,
            )
            self.certificate_doc_url = aws.upload_file(self.certificate_doc, fileUploadPath)
            self.certificate_doc = None
            super(UserEducationDetail, self).save(force_insert=False, force_update=True, using='default',
                                                  update_fields=None)


class VerifyOtp(models.Model):
    user = models.OneToOneField(
        User,
        related_name='user_who_wants_to_verify_email_or_mobile',
        on_delete=models.CASCADE,
        unique=True,
        null=False,
    )
    otp = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )


class Group(models.Model):
    """all groups"""

    name = models.CharField(
        max_length=30,
        blank=False,
        unique=True
    )
    max_num_of_vehicle_allowed = models.IntegerField(
        default=2
    )
    created_by = models.ForeignKey(
        User,
        verbose_name='created by user',
        related_name='creted_by_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name='updated by user',
        related_name='updated_by_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(
        'date joined',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )

    def __str__(self):
        return self.name


class Permission(models.Model):
    """permissions"""

    name = models.CharField(
        max_length=30,
        blank=False,
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        User,
        related_name='permission_creted_by_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        related_name='permission_updated_by_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(
        'creation date',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )


class GroupPermission(models.Model):
    """Group permissions"""

    group = models.ForeignKey(
        Group,
        related_name='group',
        null=False,
        on_delete=models.CASCADE,
    )
    permission = models.ForeignKey(
        Permission,
        related_name='permission_to_group',
        null=True,
        on_delete=models.CASCADE,
    )
    is_access = models.CharField(
        choices=constants.ACCESS,
        default='all',
        max_length=255
    )
    created_by = models.ForeignKey(
        User,
        related_name='group_permission_creted_by_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        related_name='group_permission_updated_by_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(
        'creation date',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )


class FavoriteExpert(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_who_liked_expert_id',
        on_delete=models.CASCADE,
        null=True,
    )
    expert = models.ForeignKey(
        User,
        related_name='expert_id',
        on_delete=models.CASCADE,
        null=True,
    )
    created_at = models.DateTimeField(
        'date added',
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('user', 'expert',)


class ExpertList(models.Model):
    username = models.CharField(
        'username',
        max_length=255,
        unique=True,
    )
    mobile = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    short_description = models.TextField(
        null=True,
        blank=True,
    )
    professional_title = models.CharField(
        'professional_title',
        max_length=100,
        null=True,
        blank=True,
    )
    title = models.CharField(
        choices=constants.TITLE_CHOICES,
        max_length=30,
        null=False,
        blank=False,
    )
    first_name = models.CharField(
        'first name',
        max_length=30,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        'last name',
        max_length=30,
        null=True,
        blank=True,
    )
    nick_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    user_type = models.CharField(
        choices=constants.TYPE_CHOICES,
        max_length=100,
        blank=True,
        default='customer',
    )
    biographic_info = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    user_img = models.CharField(
        "user image url",
        max_length=200,
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    email = models.CharField(
        'email address',
        max_length=255,
        blank=True,
    )
    is_verified = models.BooleanField(
        'verification status',
        default=False,
        help_text='Designates whether the user is verified or not',
    )
    email_verified = models.BooleanField(
        'email verification status',
        default=False,
        help_text='Designates whether the user email is verified or not',
    )
    mobile_verified = models.BooleanField(
        'mobile verification status',
        default=False,
        help_text='Designates whether the user mobile is verified or not',
    )
    password = models.CharField(
        'user password',
        max_length=255,
        blank=True,
        default='',
    )
    created_at = models.DateTimeField(
        'date joined',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )

    """
    additional data fields for specified users
    """
    designation = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    qualification = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    experience = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    experties = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    fb_link = models.CharField(
        "facebook profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    twitter_link = models.CharField(
        "twitter  profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    linked_link = models.CharField(
        "linkedin profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    google_link = models.CharField(
        "google profile link",
        max_length=500,
        null=True,
        blank=True,
    )
    tinode_token = models.CharField(
        "token for chat and all",
        max_length=500,
        null=True,
        blank=True,
    )
    is_favorite = models.BooleanField(
        'is users favorite expert',
        default=False,
    )
    categories = JSONField(
        null=True,
    )
    expert_score = models.IntegerField(
        default=0,
        null=True,
        blank=True,
    )
    profile_picture = models.ImageField(null=True, blank=True, )

    class Meta:
        managed = False


class Category(models.Model):
    name = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        unique=True,
    )
    logo = models.TextField(
        null=True,
        blank=True,
    )
    logo_image = models.ImageField(
        null=True,
        blank=True,
        upload_to='logo',
    )

    def logo_tag(self):
        from django.utils.html import escape
        return format_html('<img src="data:;base64,%s" alt="" style="\
        border: 1px solid #ddd; border-radius: 4px; padding: 5px; width: 150px;">' % (self.logo))

    logo_tag.short_description = 'Logo'

    def image_to_b64(self, image_file):
        try:
            with open(image_file.path, 'rb') as f:
                encoded_string = base64.b64encode(f.read()).decode("utf-8")
                return encoded_string
        except BaseException as err:
            return None

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if self.logo_image:
            base64Data = self.image_to_b64(self.logo_image)
            if base64Data:
                self.logo = self.image_to_b64(self.logo_image)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return "(" + str(self.id) + ") " + self.name


class CategoryList(models.Model):
    name = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        unique=True,
    )
    logo = models.TextField(
        null=True,
        blank=True,
    )
    is_selected = models.BooleanField(
        default=False,
    )

    class Meta:
        managed = False


class UserIntrestOrExpertise(models.Model):
    user = models.ForeignKey(
        User,
        related_name='intrested_or_expert_user',
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        Category,
        related_name='category',
        on_delete=models.CASCADE,
    )


class UserOrder(models.Model):
    user = models.ForeignKey(
        User,
        related_name='buyer',
        on_delete=models.CASCADE,
    )
    programBatch = models.ForeignKey(
        "program.ProgramBatch",
        related_name='programBatch',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        'order amount in paisa',
        max_digits=20,
        decimal_places=2,
    )
    order_id = models.CharField(
        max_length=500,
        null=True,
    )
    payment_id = models.CharField(
        max_length=500,
        null=True,
    )
    order_request = JSONField(
        null=True,
    )
    order_response_before_payment = JSONField(
        null=True,
    )
    order_response_after_payment = JSONField(
        null=True,
    )
    payment_request = JSONField(
        null=True,
    )
    payment_response_from_ui = JSONField(
        null=True,
    )
    payment_response_on_fetch = JSONField(
        null=True,
    )
    payment_status = models.CharField(
        choices=constants.PAYMENT_STATUS_CHOICES,
        max_length=100,
        default='pending',
    )
    created_at = models.DateTimeField(
        'order creation timestamp',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        'order updation timestamp',
        auto_now=True,
    )

    # id have prefi YS following 12 digit id
    def getRecieptId(self):
        reciept_id = 'YS'
        if len(str(self.id)) < 12:
            for i in range(12 - len(str(self.id))):
                reciept_id += '0'
        reciept_id += str(self.id)
        return reciept_id


class UserDeviceToken(models.Model):
    user = models.ForeignKey(
        User,
        related_name='device_user',
        on_delete=models.CASCADE,
    )
    device_token = models.CharField(
        max_length=500,
        null=False,
        blank=False
    )
    device = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        default='webapp',
    )
    created_at = models.DateTimeField(
        'user token creation timestamp',
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('user', 'device_token',)


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.location_name


class TimeZone(models.Model):
    timezone_id = models.AutoField(primary_key=True)
    timezone_name = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.timezone_name


class Languages(models.Model):
    language_id = models.AutoField(primary_key=True)
    language_name = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.language_name


class Expertise(models.Model):
    expertise_id = models.AutoField(primary_key=True)
    expertise_name = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.expertise_name


class ExpertTeamMember(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user',
        on_delete=models.CASCADE,

    )
    team_member_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    # role = models.CharField(max_length=50,blank=True,null=True)
    role = models.ForeignKey('Role', related_name="Role", blank=True, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, help_text="Phone number of user", blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return self.role_name


class DegreeCertification(models.Model):
    degree_id = models.AutoField(primary_key=True)
    degree_name = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return self.degree_name
