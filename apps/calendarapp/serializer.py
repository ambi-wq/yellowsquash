from rest_framework import serializers
from apps.program.models import *
from apps.webinar.models import *


class UpcomingSessionSerializer(serializers.ModelSerializer):
    program_id = serializers.IntegerField(source='programBatch.program.id')
    program_title = serializers.CharField(source='programBatch.program.title')
    session_title = serializers.CharField(source='title')

    class Meta:
        model = ProgramBatchSession
        fields = ['id', 'session_title', 'program_title', 'programBatch_id', 'program_id', 'session_date', 'start_time',
                  'end_time']


class UpcomingWebinarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webinar
        fields = ['id','title','subtitle','webinar_date','start_time','end_time']
