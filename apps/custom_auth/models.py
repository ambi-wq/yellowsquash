from django.db import models

from apps.user.models import User

class PasswordResetOtp(models.Model):

    user = models.OneToOneField(
        User,
        related_name='user_who_wants_to_reset_password',
        on_delete=models.CASCADE,
        unique=True,
        null=False,
    )
    otp = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    token = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
