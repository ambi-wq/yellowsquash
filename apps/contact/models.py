from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(
        max_length=600,
        blank=True,
        null=True,
    )
    email_id = models.CharField(
        max_length=600,
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    comment = models.TextField(
        blank=True,
        null=True
    )


    def __str__(self):
        return self.name
    