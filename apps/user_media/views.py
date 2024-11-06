import json, random, string
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework import authentication
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Media, StaticResources
from .serializer import MediaSerializer, StaticResourcesSerializer

import logging
import razorpay

from apps.common_utils.Aws import Aws

from PIL import Image


logger = logging.getLogger(__name__)



class GetMedia(generics.ListAPIView):

    queryset = Media.objects.all().order_by('-created_timestamp')
    serializer_class = MediaSerializer
    permission_classes = (AllowAny,)



class AddMedia(generics.CreateAPIView):

    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            media = Media.objects.create(
                file_name = request.data.get('file_name'),
                alt_text = request.data.get('alt_text'),
                caption = request.data.get('caption'),
                description = request.data.get('description'),
                media_file = request.FILES['file'],
                created_by = request.user,
                last_updated_by = request.user,
            )
            serializer = MediaSerializer(media, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            logger.exception("failed adding media : ", exc_info=err)
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class UpdateMedia(generics.UpdateAPIView):

    permission_classes = (AllowAny,)

    def put(self, request, media_id):
        try:
            media = Media.objects.get(id=media_id)
            if 'file_name' in request.data and request.data.get('file_name'):
                media.file_name = request.data.get('file_name')
            if 'alt_text' in request.data and request.data.get('alt_text'):
                media.alt_text = request.data.get('alt_text')
            if 'caption' in request.data and request.data.get('caption'):
                media.caption = request.data.get('caption')
            if 'description' in request.data and request.data.get('description'):
                media.description = request.data.get('description')
            if request.FILES and 'file' in request.FILES and request.FILES['file']:
                media.media_file = request.FILES['file']
            
            media.last_updated_by = request.user
            media.save()

            serializer = MediaSerializer(media, many=False)

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        except BaseException as err:
            logger.exception("failed adding media : ", exc_info=err)
            return JsonResponse({
                    'message': 'Something went wrong',
                    'error': str(err)
                },
                safe=False, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetListStaticResources(generics.ListAPIView):

    permission_classes = (AllowAny,)
    serializer_class = StaticResourcesSerializer
    queryset = StaticResources.objects.all()


class GetStaticResources(generics.RetrieveAPIView):

    # permission_classes = (AllowAny,)
    # serializer_class = StaticResourcesSerializer
    # queryset = StaticResources.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StaticResourcesSerializer
    #get all info 
    def get(self, request, slug):
        try:
            if StaticResources.objects.filter(slug = slug).exists() :
                queryset = StaticResources.objects.filter(slug = slug).first()
                serializer = StaticResourcesSerializer(queryset,many=False)
                return Response(serializer.data)
            else : 
                return JsonResponse({
                    "error" : "No data found."
                },status=status.HTTP_400_BAD_REQUEST)
        except BaseException as err:
            return JsonResponse({
                "error" : err
            })


class CreateStaticResources(generics.CreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = StaticResourcesSerializer
    queryset = StaticResources.objects.all()


class RetrieveUpdateDestroyStaticResources(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = StaticResourcesSerializer
    queryset = StaticResources.objects.all()
