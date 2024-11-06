from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import status, mixins, generics, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from apps.blog.models import Blog
from apps.program.models import *
from .serializer import *


class BlogCount(generics.ListAPIView):
    permission_classes = (AllowAny,)

    # get all info
    def get(self, request):
        print(request.user.user_type)

        count = Blog.objects.filter(status='published').count()

        # # if user is admin or expert then count will vary
        if request.user.is_authenticated:
            if request.user.user_type == 'admin':
                count = Blog.objects.exclude(status='draft').count()
            elif request.user.user_type == 'expert':
                count = Blog.objects.filter(expert_id=request.user).count()

        return JsonResponse({
            "count": count
        }, status=status.HTTP_202_ACCEPTED)


class PatientDashboard(generics.ListAPIView):
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        program = Program.objects.filter(expert=user)
        print(f"{program=}")
        batch_user = ProgramBatchUser.objects.filter(programBatch__program__in=program)
        print(batch_user)
        page = self.paginate_queryset(batch_user)
        serializer = ProgramBatchUserSerializer(batch_user, many=True)
        # return self.get_paginated_response(serializer.data[start_limit:end_limit])
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class SymptomsList(generics.ListAPIView):
    pagination_class = LimitOffsetPagination

    def get(self, request):
        symptoms = SymptomTracker.objects.all()
        page = self.paginate_queryset(symptoms)
        serializer = SymptomTrackerSerializer(symptoms, many=True)
        # return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
