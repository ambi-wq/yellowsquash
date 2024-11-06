from rest_framework import serializers
from apps.program.models import *


class ProgramBatchUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    program_title = serializers.SerializerMethodField('get_program_title')
    batch_title = serializers.SerializerMethodField('get_batch_title')
    program_id = serializers.SerializerMethodField('get_program_id')

    class Meta:
        model = ProgramBatchUser
        fields = ['id', 'user', 'programBatch', 'name','program_id','program_title','batch_title']

    def get_name(self, obj):
        name = ""
        if obj.user.first_name:
            name += obj.user.first_name + " "
        if obj.user.last_name:
            name += obj.user.last_name
        return name

    def get_program_title(self, obj):
        title = obj.programBatch.program.title
        return title

    def get_batch_title(self, obj):
        title = obj.programBatch.title
        return title

    def get_program_id(self, obj):
        return obj.programBatch.program_id


class SymptomTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomTracker
        fields = ['id', 'title']
