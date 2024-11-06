from django.db import models
from apps.user.models import *
from apps.program.models import *


# Create your models here.


class Query(models.Model):
    query_id = models.AutoField(primary_key=True)
    program_batch = models.ForeignKey(ProgramBatch, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=500)
    # attachment = models.FileField(upload_to='queries', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query


class QueryAttachments(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    attachment = models.FileField(upload_to='queries', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)

    def __str__(self):
        return self.attachment


class QueryComment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)
    liked_user = models.ManyToManyField(User, related_name='liked_user_comment', blank=True, null=True)

    def __str__(self):
        return self.comment


class QueryCommentReply(models.Model):
    reply_id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(QueryComment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reply
