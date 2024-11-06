from rest_framework import serializers
from .models import Media, StaticResources
import json
import logging


logger = logging.getLogger(__name__)


class MediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Media
        fields = ['id', 'file_name', 'alt_text', 'caption', 'description', 'media_file', 'file_url', 'created_timestamp', 'last_modified_timestamp', 
        'created_by', 'last_updated_by' ]


class StaticResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticResources
        fields = "__all__"
