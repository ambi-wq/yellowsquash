from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Query)
admin.site.register(QueryComment)
admin.site.register(QueryCommentReply)

