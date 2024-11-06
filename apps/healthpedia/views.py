from django.shortcuts import render
from rest_framework import views, generics, filters, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import *
from apps.user.models import *
from apps.blog.models import *
from apps.videos.models import *

# Create your views here.
from ..common_utils.standard_response import success_response


class BlogList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        queryset = Blog.objects.all().order_by('-created_at')

        if category:
            category = [int(c) for c in category.split(',')]
            queryset = queryset.filter(categories__in=category).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = BlogListSerializer(queryset, many=True, context={'user': request.user})
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)


class VideoList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        queryset = Video.objects.all().order_by('-created_at')

        if category:
            category = [int(c) for c in category.split(',')]
            queryset = queryset.filter(category__in=category).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = VideoListSerializer(queryset, many=True, context={'user': request.user})
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)
