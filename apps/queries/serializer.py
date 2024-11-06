from rest_framework import serializers

from yellowsquash import settings
from .models import *


class QueryAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryAttachments
        fields = ['attachment_id', 'attachment']


class QuerySerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField('get_attachments')

    class Meta:
        model = Query
        fields = ['query_id', 'query', 'created_at', 'update_at', 'program_batch', 'user', 'attachments']

    def get_attachments(self, query):
        attachments = QueryAttachments.objects.filter(query=query)
        return QueryAttachmentSerializer(attachments, many=True).data


class QueryCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryComment
        fields = "__all__"


class QueryCommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryCommentReply
        fields = "__all__"


class AllQueriesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    profile_pic = serializers.SerializerMethodField('get_profile_pic')
    update_date = serializers.SerializerMethodField('get_update_date')
    answer = serializers.SerializerMethodField('get_answer')

    class Meta:
        model = Query
        fields = ['query_id', 'query', 'update_at', 'user_id', 'name', 'profile_pic', 'update_date',
                  'answer']

    def get_name(self, obj):
        name = ""
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name
        return name

    def get_profile_pic(self, obj):
        if obj.user.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.user.profile_picture))
            return profile_picture
        return ""

    def get_update_date(self, obj):
        time = datetime.now()

        if obj.update_at.day == time.day:
            if time.minute - obj.update_at.minute == 0:
                return str(time.second - obj.update_at.second) + " seconds ago"
            if time.hour - obj.update_at.hour == 0:
                return str(time.minute - obj.update_at.minute) + " minutes ago"
            return str(time.hour - obj.update_at.hour) + " hours ago"
        elif obj.update_at.month == time.month:
            if time.day - obj.update_at.day == 7:
                return "1 week ago"
            return str(time.day - obj.update_at.day) + " days ago"
        elif obj.update_at.year == time.year:
            return str(time.month - obj.update_at.month) + " months ago"

        return obj.update_at

    def get_answer(self, obj):
        count = QueryComment.objects.filter(query=obj).count()
        if count == 0:
            return "No answer yet"
        else:
            return str(count) + " answers"


class ReplyDetailsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    profile_pic = serializers.SerializerMethodField('get_profile_pic')
    update_date = serializers.SerializerMethodField('get_update_date')
    usertype = serializers.SerializerMethodField('get_usertype')

    class Meta:
        model = QueryCommentReply
        fields = ['reply_id', 'reply', 'user_id', 'name', 'profile_pic', 'update_at', 'update_date', 'usertype']

    def get_name(self, obj):
        name = ""
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name
        return name

    def get_profile_pic(self, obj):
        if obj.user.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.user.profile_picture))
            return profile_picture
        return ""

    def get_update_date(self, obj):
        time = datetime.now()

        if obj.update_at.day == time.day:
            if time.minute - obj.update_at.minute == 0:
                return str(time.second - obj.update_at.second) + " seconds ago"
            if time.hour - obj.update_at.hour == 0:
                return str(time.minute - obj.update_at.minute) + " minutes ago"
            return str(time.hour - obj.update_at.hour) + " hours ago"
        elif obj.update_at.month == time.month:
            if time.day - obj.update_at.day == 7:
                return "1 week ago"
            return str(time.day - obj.update_at.day) + " days ago"
        elif obj.update_at.year == time.year:
            return str(time.month - obj.update_at.month) + " months ago"

        return obj.update_at

    def get_usertype(self, obj):
        return obj.user.user_type


class CommentDetailsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    profile_pic = serializers.SerializerMethodField('get_profile_pic')
    update_date = serializers.SerializerMethodField('get_update_date')
    usertype = serializers.SerializerMethodField('get_usertype')
    total_like = serializers.SerializerMethodField('get_total_like')
    reply = serializers.SerializerMethodField('get_reply')

    class Meta:
        model = QueryComment
        fields = ['comment_id', 'comment', 'user_id', 'name', 'profile_pic', 'update_at', 'update_date', 'usertype',
                  'total_like', 'reply']

    def get_name(self, obj):
        name = ""
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name
        return name

    def get_profile_pic(self, obj):
        if obj.user.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.user.profile_picture))
            return profile_picture
        return ""

    def get_update_date(self, obj):
        time = datetime.now()

        if obj.update_at.day == time.day:
            if time.minute - obj.update_at.minute == 0:
                return str(time.second - obj.update_at.second) + " seconds ago"
            if time.hour - obj.update_at.hour == 0:
                return str(time.minute - obj.update_at.minute) + " minutes ago"
            return str(time.hour - obj.update_at.hour) + " hours ago"
        elif obj.update_at.month == time.month:
            if time.day - obj.update_at.day == 7:
                return "1 week ago"
            return str(time.day - obj.update_at.day) + " days ago"
        elif obj.update_at.year == time.year:
            return str(time.month - obj.update_at.month) + " months ago"

        return obj.update_at

    def get_usertype(self, obj):
        return obj.user.user_type

    def get_total_like(self, obj):
        return obj.liked_user.count()

    def get_reply(self, obj):
        reply = QueryCommentReply.objects.filter(comment=obj)
        serializers = ReplyDetailsSerializer(reply, many=True).data
        return serializers


class QueryDetailsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    profile_pic = serializers.SerializerMethodField('get_profile_pic')
    update_date = serializers.SerializerMethodField('get_update_date')
    comment = serializers.SerializerMethodField('get_comment')

    class Meta:
        model = Query
        fields = ['query_id', 'query', 'user_id', 'name', 'profile_pic', 'update_at', 'update_date', 'comment']

    def get_name(self, obj):
        name = ""
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name
        return name

    def get_profile_pic(self, obj):
        if obj.user.profile_picture:
            profile_picture = os.path.join(settings.MEDIA_URL, str(obj.user.profile_picture))
            return profile_picture
        return ""

    def get_update_date(self, obj):
        time = datetime.now()

        if obj.update_at.day == time.day:
            if time.minute - obj.update_at.minute == 0:
                return str(time.second - obj.update_at.second) + " seconds ago"
            if time.hour - obj.update_at.hour == 0:
                return str(time.minute - obj.update_at.minute) + " minutes ago"
            return str(time.hour - obj.update_at.hour) + " hours ago"
        elif obj.update_at.month == time.month:
            if time.day - obj.update_at.day == 7:
                return "1 week ago"
            return str(time.day - obj.update_at.day) + " days ago"
        elif obj.update_at.year == time.year:
            return str(time.month - obj.update_at.month) + " months ago"

        return obj.update_at

    def get_comment(self, obj):
        comment = QueryComment.objects.filter(query=obj)
        serializers = CommentDetailsSerializer(comment, many=True).data
        return serializers
