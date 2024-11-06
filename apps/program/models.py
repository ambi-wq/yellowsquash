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


class Program(models.Model):
    title = models.CharField(
        max_length=100,
        blank=False,
        null=True
    )
    slug = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    rating = models.DecimalField(
        blank=False,
        null=True,
        max_digits=2,
        decimal_places=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    intro_video_url = models.CharField(
        "program intro video url",
        max_length=200,
        blank=False,
        null=True
    )
    image_url = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    thumbnail_image = models.FileField(
        "temporary field for getting image from admin panel (Ideal Size: 500px X 345px)",
        null=True,
        blank=True,
    )
    expert = models.ForeignKey(
        User,
        related_name='expert_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    auther = models.ForeignKey(
        User,
        related_name='auther_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    html_description = models.TextField(
        blank=False,
        null=True
    )
    speciality = models.CharField(
        blank=False,
        null=True,
        max_length=200
    )
    price = models.DecimalField(
        'program cost',
        max_digits=20,
        decimal_places=2,
        null=True,
    )
    session_count = models.IntegerField(
        'number of sessions',
        null=True,
    )
    duration_in_weeks = models.IntegerField(
        'duration in weeks',
        null=True,
    )
    start_date = models.DateField(
        'start date',
        default=timezone.now,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )
    chat_group_key = models.CharField(
        "auto genrated group chat key(Don't Update Manually After Creation)",
        max_length=50,
        null=True,
        blank=True,
    )
    category = models.ManyToManyField(
        Category,
        through='ProgramCategory',
        related_name='program_categories',
    )

    def __str__(self):
        return self.title

    def get_current_batch_offer_price(self):
        self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now())
        if self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).exists():
            if self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).order_by(
                    'batch_start_date').first().offer_price:
                return self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).order_by(
                    'batch_start_date').first().offer_price
            else:
                return self.price
        else:
            return self.price

    def get_current_batch(self):
        if self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).exists():
            return self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).order_by(
                'batch_start_date').first()
        else:
            return None

    def get_current_batch_id(self):
        if self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).exists():
            return self.programs_batches.filter(program=self, batch_start_date__gte=datetime.now()).order_by(
                'batch_start_date').first().id
        else:
            return None

    # overriding of this method is neccessary becuse we need to uodate key on create from admin panel of django
    def save(self, *args, **kwargs):
        isCreateCall = self.pk is None  # if its update call then we don't need to upadte group chat key
        super(Program, self).save(*args, **kwargs)

        if self.slug is None:
            self.slug = slugify(self.title) + "-" + str(int(time.time()))

        if self.thumbnail_image:
            aws = Aws()
            fileUploadPath = AwsFilePath.programMediaFilePath(
                resource_file_name=self.thumbnail_image.name,
            )
            self.image_url = aws.upload_file(self.thumbnail_image, fileUploadPath)
            self.thumbnail_image = None
            super(Program, self).save(force_insert=False, force_update=True, using='default', update_fields=None)
        # todo make new chat group and update its tinode group nanme into database
        if isCreateCall:
            try:
                # TODO: update admin token for real admin
                adminUserToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0aW5vZGVfdXNlcl9pZCI6InVzclFkR2gwOW1jOTVnIiwidXNlcm5hbWUiOiJwcmF5YXMxNjMiLCJwYXNzd29yZCI6InNlY3VyZWRAY2Nlc3MifQ.gE8Slpk23961nNPWLgsPgqSb_JdWTXb3r0BTF1LA9vQ'

                # create chat group for program
                tinodeNew = Tinode()
                tinodeChatGroupKey = tinodeNew.CreateChatGroup(
                    adminUserToken=adminUserToken,
                    userToken=self.expert.tinode_token,
                    groupName=self.title,
                    tags=["program"],  # TODO: update according to needs
                )

                # AddExpertToChatGroup if group key already generated
                if tinodeChatGroupKey:
                    self.chat_group_key = tinodeChatGroupKey
                    logger.info(tinodeChatGroupKey)
                    self.save()

                    # add expert to chat group
                    tinodeNew = Tinode()  # refresh object
                    tinodeNew.AddUserToChatGroup(
                        adminUserToken=adminUserToken,
                        userToken=self.expert.tinode_token,
                        tinodeGroupkey=tinodeChatGroupKey
                    )

                else:
                    logger.info("tinode chat group genration failed for the program : {0}".format(self.title))

            except BaseException as err:
                logger.exception("Failed genrating group chat key : ", exc_info=err)

    def delete(self, *args, **kwargs):

        # before deleting program delete its group
        if self.chat_group_key:
            try:
                # TODO: update admin token for real admin
                adminUserToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0aW5vZGVfdXNlcl9pZCI6InVzclFkR2gwOW1jOTVnIiwidXNlcm5hbWUiOiJwcmF5YXMxNjMiLCJwYXNzd29yZCI6InNlY3VyZWRAY2Nlc3MifQ.gE8Slpk23961nNPWLgsPgqSb_JdWTXb3r0BTF1LA9vQ'
                tinodeNew = Tinode()
                tinodeChatGroupKey = tinodeNew.DeleteProgramChatGroup(
                    groupAdminToken=adminUserToken,
                    tinodeGroupkey=self.chat_group_key,
                )
            except BaseException as err:
                logger.exception("Failed deleting program chat group for title : {0}".format(self.title), exc_info=err)

        super(Program, self).delete(*args, **kwargs)


# virtual table for users to get all programs data faster
class UserProgramList(models.Model):
    title = models.CharField(
        max_length=100,
    )
    rating = models.DecimalField(
        blank=True,
        max_digits=2,
        decimal_places=1,
    )
    intro_video_url = models.CharField(
        "program into video url",
        max_length=200,
        blank=True
    )
    image_url = models.CharField(
        max_length=100,
        blank=True
    )
    expert = models.ForeignKey(
        User,
        related_name='program_expert_user',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    auther = models.ForeignKey(
        User,
        related_name='program_auther_user',
        null=True,
        on_delete=models.DO_NOTHING,
    )
    html_description = models.TextField(
        blank=True,
    )
    offer_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        'program cost',
        max_digits=20,
        decimal_places=2,
        null=True,
    )
    session_count = models.IntegerField(
        'number of sessions',
        null=True,
    )
    duration_in_weeks = models.IntegerField(
        'duration in weeks',
        null=True,
    )
    start_date = models.DateField(
        'start date',
        default=timezone.now,
    )
    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default='active',
        max_length=10
    )
    chat_group_key = models.CharField(
        "auto genrated group chat key(Don't Update Manually After Creation)",
        max_length=50,
        null=True,
        blank=True,
    )
    is_favorite = models.BooleanField(
        'is users favorite program',
        default=False,
    )
    is_subscribed = models.CharField(
        choices=constants.PAYMENT_STATUS,
        max_length=100,
        default='inactive'
    )
    experties = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    batch = models.ForeignKey(
        "ProgramBatch",
        null=False,
        on_delete=models.DO_NOTHING,
    )

    # category = models.ManyToManyField(
    #     Category,
    #     related_name='userprogramList_categories',
    # )
    def __str__(self):
        return self.title

    class Meta:
        managed = False


class Overview(models.Model):
    title = models.CharField(
        'overview title',
        max_length=100,
        blank=True,
    )
    header_image_link = models.CharField(
        'header image link',
        max_length=100,
        blank=True,
    )
    description = models.TextField(
        'overview description',
        blank=True,
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    title = models.CharField(
        'curriculum title',
        max_length=100,
        blank=True,
    )

    description = models.TextField(
        'review description',
        blank=True,
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        blank=True
    )
    rating = models.IntegerField(
        max_length=10,
        blank=True
    )

    created_date = models.DateTimeField(
        'Created date',
        auto_now_add=True
    )
    status = models.CharField(
        max_length=100,
        choices=constants.PROGRAM_REVIEW_STATUS,
        default='under_review',

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )

    like = models.ManyToManyField(User,blank=True,null=True,related_name='review_like')

    def __str__(self):
        return self.title


class ReviewFiles(models.Model):
    files = models.FileField(upload_to='program_review', blank=True, null=True)
    review = models.ForeignKey(Review, blank=True, null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.review


class FrequentlyAskedQuestion(models.Model):
    question = models.TextField(
        'question',
    )
    answer = models.TextField(
        'answer',
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.question


class ProgramBatchUser(models.Model):
    programBatch = models.ForeignKey(
        "ProgramBatch",
        on_delete=models.CASCADE,
        blank=False,
    )
    subscription_date = models.DateTimeField(
        'Subscription date',
        default=timezone.now,
        null=True,
    )
    user = models.ForeignKey(
        User,
        related_name='customer_id',
        on_delete=models.CASCADE,
        null=True,
    )
    status = models.CharField(
        max_length=100,
        choices=constants.PAYMENT_STATUS,
        default='inactive',
    )

    class Meta:
        unique_together = ('programBatch', 'user',)

    def save(self, *args, **kwargs):
        isCreateCall = self.pk is None  # if its update call then we don't need to upadte group chat key
        super(ProgramBatchUser, self).save(*args, **kwargs)
        # todo make new chat group and update its tinode group nanme into database
        if isCreateCall:
            # insert chat token if available
            try:
                adminUserToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0aW5vZGVfdXNlcl9pZCI6InVzclFkR2gwOW1jOTVnIiwidXNlcm5hbWUiOiJwcmF5YXMxNjMiLCJwYXNzd29yZCI6InNlY3VyZWRAY2Nlc3MifQ.gE8Slpk23961nNPWLgsPgqSb_JdWTXb3r0BTF1LA9vQ'
                tinodeNew = Tinode()
                tinodeNew.AddUserToChatGroup(
                    adminUserToken=adminUserToken,
                    userToken=self.user.tinode_token,
                    tinodeGroupkey=self.programBatch.program.chat_group_key
                )

                # connect expert to directly user also
                tinodeNew = Tinode()
                tinodeNew.ConnectUser1ToUser2(
                    user1Token=self.programBatch.program.expert.tinode_token,
                    user2Token=self.user.tinode_token
                )

            except BaseException as err:
                logger.exception("Failed getting tinode token : ", exc_info=err)

    def delete(self, *args, **kwargs):

        # before removing program user remove him from char group
        if self.programBatch and self.programBatch.program and self.programBatch.program.chat_group_key and self.user and self.user.tinode_token:
            try:
                tinodeNew = Tinode()
                tinodeChatGroupKey = tinodeNew.LeaveUserGroupChat(
                    userToken=self.user.tinode_token,
                    tinodeGroupkey=self.program.chat_group_key,
                )
            except BaseException as err:
                logger.exception("Failed deleting program chat group for title : {0}".format(self.title), exc_info=err)

        super(ProgramBatchUser, self).delete(*args, **kwargs)


class FavoriteProgram(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_who_liked_program_id',
        on_delete=models.CASCADE,
        null=True,
    )
    program = models.ForeignKey(
        Program,
        related_name='favorite_program_id',
        on_delete=models.CASCADE,
        null=True,
    )
    created_at = models.DateTimeField(
        'date added',
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('user', 'program',)


class ProgramCategory(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='programs_for_category',
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        Category,
        related_name='program_category',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (("program", "category"),)

    def __str__(self) -> str:
        return f'{self.category.name}'


class ProgramBatch(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='programs_batches',
        null=False,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        "batch description",
        max_length=100,
        null=True,
        blank=True,
    )
    start_time = models.TimeField(
        "default batch session start timing",
        null=False,
        blank=False,
        default='07:00',
    )
    end_time = models.TimeField(
        "default batch session end timing",
        null=False,
        blank=False,
        default='09:00',
    )
    batch_start_date = models.DateField(
        'batch start date',
        null=False,
        default=datetime.now
    )
    batch_end_date = models.DateField(
        'batch end date',
        null=True,
    )
    scheduling_strategy = models.CharField(
        choices=constants.SESSION_SCHEDULE_TYPE,
        max_length=10,
        default="daily",
        null=False,
        blank=False,
    )
    scheduled_days_of_week = ArrayField(
        models.CharField(
            choices=constants.WEEK_DAYS,
            max_length=12,
            default="Monday",
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        help_text="""
        This is Only Applicable if scheduling_strategy is selected WEEKLY
        """,
    )
    scheduled_day_of_month = models.IntegerField(
        "day of month",
        choices=constants.DAY_OF_MONTH,
        default=1,
        null=True,
        blank=True,
        help_text="""
        This is Only Applicable if <b>scheduling_strategy</b> is selected <b>MONTHLY</b> <br>
        <b>Warning</b>: For dates like 29,30,31 if not available in any month then last day of month will be considered
        """,
    )
    created_at = models.DateTimeField(
        'session creation date',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )
    batch_status = models.CharField(
        choices=constants.BATCH_STATUS,
        default='open',
        max_length=10,
        null=False,
        blank=False,
    )
    offer_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )
    meet_link = models.CharField(
        "zoom meeting link",
        max_length=500,
        null=True,
        blank=True
    )
    capacity = models.IntegerField(
        null=False,
        blank=False,
        default=2
    )
    additional_start_date = models.DateField(
        null=True,
    )
    additional_days = models.IntegerField(
        null=False,
        blank=False,
        default=2
    )

    def __str__(self):
        if self.title:
            return self.title
        else:
            return 'N/A'

    def getSessionDates(self, sessionCount=0):

        sessionDates = []

        # if it is requested without session count then consider its current sessions
        if not sessionCount:
            sessionCount = ProgramBatchSession.objects.filter(programBatch=self.id).count()

        # return blank if there is no sessions available
        if not sessionCount:
            return sessionDates

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        """
        once : only one session in program
        daily : daily session for program
        weekly : will be considered daily if scheduled_days_of_week is not selected
        monthly : will be considered daily if scheduled_day_of_month is not selected
        default : for unexpect input it will be considered daily
        """
        try:
            batchEndDateTemp = self.batch_start_date + timedelta(
                days=1461)  # possible end date can be after 4 years of start (365 + 365 + 365 + 366)
            if self.scheduling_strategy == 'once':
                sessionDates.append(self.batch_start_date)
            elif self.scheduling_strategy == 'daily':
                for single_date in daterange(self.batch_start_date, batchEndDateTemp):
                    sessionDates.append(single_date)
                    if len(sessionDates) >= sessionCount:
                        break
            elif self.scheduling_strategy == 'weekly' and self.scheduled_days_of_week:
                for single_date in daterange(self.batch_start_date, batchEndDateTemp):
                    if single_date.strftime("%A") in self.scheduled_days_of_week:
                        sessionDates.append(single_date)
                        if len(sessionDates) >= sessionCount:
                            break
            elif self.scheduling_strategy == 'monthly' and self.scheduled_day_of_month:
                startMonth = self.batch_start_date.month
                startyear = self.batch_start_date.year
                sessionMonth = startMonth
                sessionYear = startyear
                while sessionMonth <= 12:
                    try:
                        sessionDates.append(datetime(sessionYear, sessionMonth, self.scheduled_day_of_month))
                    except ValueError:
                        next_month = datetime(sessionYear, sessionMonth, 28) + timedelta(days=4)
                        last_day_of_month = next_month - timedelta(days=next_month.day)
                        sessionDates.append(datetime(sessionYear, sessionMonth, last_day_of_month.day))

                    if len(sessionDates) >= sessionCount:
                        break

                    sessionMonth += 1
                    if sessionMonth == 12:
                        sessionMonth = 1
                        sessionYear += 1
            else:
                for single_date in daterange(self.batch_start_date, batchEndDateTemp):
                    sessionDates.append(single_date)
                    if len(sessionDates) >= sessionCount:
                        break
        except BaseException as err:
            print(err)

        return sessionDates

    def save(self, *args, **kwargs):

        isCreateCall = self.pk is None  # if its update call then we don't need to upadte group chat key

        # if there is no price mentioned on batch then use program price
        if not self.offer_price:
            self.offer_price = self.program.price

        super(ProgramBatch, self).save(*args, **kwargs)

        # session and resouces will be replicated once with program on the time of batch creation
        if isCreateCall:
            # print(ProgramBatch.objects.filter(program=self.program).order_by('id').values_list('id').query)
            batches = list(ProgramBatch.objects.filter(program=self.program).order_by('id').values_list('id'))
            print(batches)
            if len(batches) > 0:
                batch_id = batches[-2] if len(batches) > 1 else batches[-1]
                programBatchSessions = ProgramBatchSession.objects.filter(programBatch=batch_id,
                                                                          session_type='permanent').order_by(
                    'sequence_num')
                print('bi', batch_id, programBatchSessions, programBatchSessions.count(), '\n',
                      programBatchSessions.query)
                numberOfSessionsToBePlan = programBatchSessions.count()
                sessionDates = self.getSessionDates(numberOfSessionsToBePlan)

                programSessionIndex = 0
                for pbs in programBatchSessions:
                    print('for', pbs.id)
                    if len(sessionDates) > programSessionIndex:
                        programBatchSession = ProgramBatchSession.objects.create(
                            title=pbs.title,
                            description=pbs.description,
                            sequence_num=pbs.sequence_num,
                            duration=pbs.duration,
                            session_type=pbs.session_type,
                            programBatch=self,
                            session_date=self.batch_start_date,  # datetime.now().date(),
                            start_time=self.start_time,
                            end_time=self.end_time,
                        )
                        programSessionResources = ProgramBatchSessionResource.objects.filter(programBatchSession=pbs)
                        if programSessionResources.count() > 0:
                            for programSessionResource in programSessionResources:
                                aws = Aws()
                                programBatchSessionResource = ProgramBatchSessionResource.objects.create(
                                    title=programSessionResource.title,
                                    description=programSessionResource.description,
                                    doc_type=programSessionResource.doc_type,
                                    doc_url=aws.copy_file(programSessionResource.doc_url,
                                                          AwsFilePath.programBatchSessionResourcePath(
                                                              program_batch_id=self.id,
                                                              batch_session_id=programBatchSession.id,
                                                              resource_file_name=
                                                              programSessionResource.doc_url.split('/')[
                                                                  -1] if programSessionResource.doc_url is not None else programSessionResource.doc_url,
                                                          )),
                                    programBatchSession=programBatchSession
                                )
                                print(programBatchSessionResource)

                    programSessionIndex += 1

                # if sessionDates:
                self.batch_end_date = self.batch_start_date  # programBatchSessions.last().session_date

        else:
            programBatchSessions = ProgramBatchSession.objects.filter(programBatch=self).order_by('sequence_num')
            sessionDates = self.getSessionDates()

            programBatchSessionIndex = 0
            if programBatchSessions:
                for programBatchSession in programBatchSessions:
                    if len(sessionDates) > programBatchSessionIndex:
                        programBatchSession.session_date = sessionDates[programBatchSessionIndex]
                        programBatchSession.save()

                    programBatchSessionIndex += 1
                self.batch_end_date = programBatchSessions.last().session_date

        self.additional_start_date = self.batch_start_date + timedelta(self.additional_days)
        super(ProgramBatch, self).save(*args, **kwargs)


class Session(models.Model):
    title = models.CharField(
        "session title",
        max_length=100,
        null=True,
        blank=True,
    )
    description = models.TextField(
        "session description",
        null=True,
        blank=True,
    )
    sequence_num = models.IntegerField(
        'order number of session',
    )
    duration = models.IntegerField(
        'duration in minutes',
        null=False,
    )
    session_type = models.CharField(
        choices=constants.SESSION_TYPE,
        max_length=10,
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(
        'session creation date',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class Resource(models.Model):
    title = models.CharField(
        "resource title",
        max_length=100,
        null=True,
        blank=True,
    )
    description = models.TextField(
        "resource description",
        null=True,
        blank=True,
    )
    doc_file = models.FileField(
        "temporary filed for getting file from admin panel",
        null=True,
        blank=True,
    )
    doc_type = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        editable=False,
    )
    doc_url = models.CharField(
        "actual doc file url",
        max_length=150,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        'session creation date',
        auto_now_add=True,
    )
    last_updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class ProgramSession(Session):
    program = models.ForeignKey(
        Program,
        related_name='programs_sessions',
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (("program", "sequence_num"),)


class ProgramSessionResource(Resource):
    programSession = models.ForeignKey(
        ProgramSession,
        related_name='programs_sessions_resources',
        null=True,
        on_delete=models.CASCADE,
        editable=True,
    )
    programBatch = models.ForeignKey(
        ProgramBatch,
        related_name='programs_sessions_batch',
        null=True,
        on_delete=models.CASCADE,
        editable=True,
    )
    program = models.ForeignKey(
        Program,
        related_name='programs',
        null=True,
        on_delete=models.CASCADE,
        editable=True,
    )

    def save(self, *args, **kwargs):
        super(ProgramSessionResource, self).save(*args, **kwargs)
        if self.doc_file:
            aws = Aws()
            fileUploadPath = AwsFilePath.programSessionResourcePath(
                program_id=self.programSession.program_id,
                session_id=self.programSession.id,
                resource_file_name=self.doc_file.name,
            )
            self.doc_url = aws.upload_file(self.doc_file, fileUploadPath)
            self.doc_type = self.doc_file.name.split(".")[-1]
            super(ProgramSessionResource, self).save(*args, **kwargs)


class ProgramBatchSession(Session):
    programBatch = models.ForeignKey(
        ProgramBatch,
        related_name='programs_batch_sessions',
        null=False,
        on_delete=models.CASCADE,
        editable=True,
    )
    session_date = models.DateField(
        'scheduled session date',
        null=False,
    )
    start_time = models.TimeField(
        "session start time",
        null=False,
        blank=False,
    )
    end_time = models.TimeField(
        "session end time",
        null=False,
        blank=False,
    )
    actual_start_datetime = models.DateTimeField(
        "actual start date time",
        null=True,
        blank=True
    )

    class Meta:
        unique_together = (("programBatch", "sequence_num"),)


class ProgramBatchSessionResource(Resource):
    programBatchSession = models.ForeignKey(
        ProgramBatchSession,
        related_name='programs_batch_session_resources',
        null=False,
        on_delete=models.CASCADE,
        editable=False,
    )

    def save(self, *args, **kwargs):
        super(ProgramBatchSessionResource, self).save(*args, **kwargs)
        if self.doc_file:
            aws = Aws()
            fileUploadPath = AwsFilePath.programBatchSessionResourcePath(
                program_batch_id=self.programBatchSession.programBatch_id,
                batch_session_id=self.programBatchSession.id,
                resource_file_name=self.doc_file.name,
            )
            self.doc_url = aws.upload_file(self.doc_file, fileUploadPath)
            self.doc_type = self.doc_file.name.split(".")[-1]
            super(ProgramBatchSessionResource, self).save(*args, **kwargs)


class UserPaymentDetail(models.Model):
    first_name = models.CharField(
        max_length=100,
        blank=True
    )
    last_name = models.CharField(
        max_length=100,
        blank=True
    )
    mobile = models.CharField(
        max_length=100,
        blank=True
    )
    email_id = models.CharField(
        max_length=100,
        blank=True
    )
    flat_or_house_no = models.CharField(
        max_length=100,
        blank=True
    )
    stret_or_landmark = models.CharField(
        max_length=100,
        blank=True
    )
    town_city_dist = models.CharField(
        max_length=100,
        blank=True
    )
    state = models.CharField(
        max_length=100,
        blank=True
    )
    country = models.CharField(
        max_length=100,
        blank=True
    )
    pincode = models.CharField(
        max_length=100,
        blank=True
    )
    gst_no = models.CharField(
        max_length=100,
        blank=True
    )
    aadhar_no = models.CharField(
        max_length=100,
        blank=True
    )
    pan_no = models.CharField(
        max_length=100,
        blank=True
    )
    payment_type = models.CharField(
        choices=constants.PAYMENT_TYPE,
        max_length=100,
        default='bank',
        blank=True
    )
    program_price = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    batch = models.ForeignKey(
        ProgramBatch,
        null=False,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    payment_screen_short = models.FileField(
        'payment screen short',
        null=True,
        blank=True
    )
    payment_screen_short_url = models.CharField(
        max_length=1000,
        blank=True,
    )
    created_at = models.DateField(
        'created date',
        auto_now=True
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    razorpay_payment_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    razorpay_signature = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def screen_short(self):
        from django.utils.html import escape
        return format_html('<img src="%s" width="500px"/>' % (self.payment_screen_short_url))

    screen_short.short_description = 'Screen Short'
    screen_short.allow_tags = True

    def __str__(self):
        return self.first_name


from django.db import models
import random
import string

DISCOUNT_CHOICES = (
    ('Fixed', 'Fixed'),
    ('Percentage', 'Percentage')
)


class Discount(models.Model):
    STATUS = (
        ('Active', "Active"),
        ('Deactive', "Deactive")
    )
    code = models.CharField(max_length=20, blank=True, null=True)
    total_redemption_limit = models.IntegerField(blank=True, null=True)
    is_unlimited_redemption = models.BooleanField(default=False)
    additional_info = models.TextField()
    valid_from_timestamp = models.DateTimeField()
    valid_till_stamp = models.DateTimeField()
    discount = models.CharField(max_length=50, null=True, blank=True)
    discount_type = models.CharField(choices=DISCOUNT_CHOICES, max_length=20)
    if_percentage_max_limit_per_tx = models.IntegerField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=20)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        super(Discount, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} - {self.status}'


class DiscountStatistics(models.Model):
    STATUS = (
        ('Applied', "Applied"),
        ('Rejected', "Rejected")
    )
    discount_applied_timestamp = models.DateTimeField()
    amount = models.FloatField()
    discount_amount = models.FloatField()
    amount_after_discount = models.FloatField()
    program = models.ForeignKey(
        Program,
        null=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        User,
        related_name='program_user',
        null=True,
        on_delete=models.SET_NULL,
    )
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=20)

    def __str__(self):
        return f'{self.amount} - {self.discount_amount} - {self.status}'


class ProgramTask(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='program_tasks',
        null=False,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        "task title",
        max_length=200,
        null=False,
        blank=False,
    )
    desc = models.CharField(
        "task description",
        max_length=200,
        null=True,
        blank=True,
    )
    task_time = models.IntegerField(
        "task timing (in Minutes)",
        null=False,
        blank=False
    )


class ActionTaskUserProgram(models.Model):
    user = models.ForeignKey(
        User,
        related_name='action_user',
        on_delete=models.CASCADE,
        null=True,
    )
    task = models.ForeignKey(
        ProgramTask,
        related_name='task_action',
        on_delete=models.CASCADE,
        null=True,
    )
    program = models.ForeignKey(
        Program,
        related_name='action_program_id',
        on_delete=models.CASCADE,
        null=True,
    )
    created_at = models.DateTimeField(
        'date added',
        auto_now_add=True,
    )
    status = models.TextField()


class LevelTracker(models.Model):
    title = models.CharField(
        'title',
        max_length=200,
    )

    icon_url = models.CharField(
        max_length=200,
    )

    def __str__(self):
        return self.title


class LevelTrackerTag(models.Model):
    tag = models.CharField(
        max_length=50,
    )

    level_tracker = models.ForeignKey(
        LevelTracker,
        related_name='level_tracker_tag',
        on_delete=models.CASCADE,
        null=True,
    )


class LevelTrackerValueType(models.Model):
    title = models.CharField(
        max_length=200,
    )

    unit = models.CharField(
        max_length=100,
    )

    initial_value = models.IntegerField(
        null=True,
        blank=True
    )

    level_tracker = models.ForeignKey(
        LevelTracker,
        related_name='level_tracker_value',
        on_delete=models.CASCADE,
        null=True,
    )


class ProgramLevelTracker(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='program_level_tracker',
        on_delete=models.CASCADE,
        null=True,
    )
    level_tracker = models.ForeignKey(
        LevelTracker,
        related_name='level_tracker_program',
        on_delete=models.CASCADE,
        null=True,
    )


class ProgramLevelValue(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='program_level_value_tracker',
        on_delete=models.CASCADE,
        null=True,
    )
    level_tracker = models.ForeignKey(
        LevelTracker,
        related_name='level_tracker_value_program',
        on_delete=models.CASCADE,
        null=True,
    )
    tag = models.ForeignKey(
        LevelTrackerTag,
        related_name='program_level_value_type_tag',
        on_delete=models.CASCADE,
        null=True,
    )
    user = models.ForeignKey(
        User,
        related_name='value_type_user',
        on_delete=models.CASCADE,
        null=True,
    )

    date = models.DateTimeField()

    # class Meta:
    # unique_together = ('user', 'program', 'task')


class ProgramLevelValueType(models.Model):
    program_level = models.ForeignKey(
        ProgramLevelValue,
        related_name='program_level_value',
        on_delete=models.CASCADE,
        null=True,
    )
    value_type = models.ForeignKey(
        LevelTrackerValueType,
        related_name='program_level_value_type',
        on_delete=models.CASCADE,
        null=True,
    )

    value = models.FloatField()


class SymptomTracker(models.Model):
    title = models.CharField(
        'title',
        max_length=200,
    )

    def __str__(self):
        return self.title


class ProgramSymptomTracker(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='program_symptom_tracker',
        on_delete=models.CASCADE,
        null=True,
    )
    symptom_tracker = models.ForeignKey(
        SymptomTracker,
        related_name='symptom_tracker_program',
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        unique_together = ('program', 'symptom_tracker',)


class ProgramSymptomTrackerValueDate(models.Model):
    program = models.ForeignKey(
        Program,
        related_name='program_symptom_tracker_value_date',
        on_delete=models.CASCADE,
        null=True,
    )
    user = models.ForeignKey(
        User,
        related_name='symptom_value_user',
        on_delete=models.CASCADE,
        null=True,
    )
    date = models.DateTimeField()
    frequency = models.CharField(max_length=100)


class ProgramSymptomTrackerValue(models.Model):
    program_symptom_tracker_value_date = models.ForeignKey(
        ProgramSymptomTrackerValueDate,
        related_name='program_symptom_tracker_value_date',
        on_delete=models.CASCADE,
        null=True,
    )
    symptom = models.ForeignKey(
        SymptomTracker,
        related_name='symptom_tracker_program_value',
        on_delete=models.CASCADE,
        null=True,
    )

    value = models.FloatField()
