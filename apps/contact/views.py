from django.shortcuts import render
from .serializer import ContactSerializer
from rest_framework import generics, status
from .models import Contact
from django.http import JsonResponse,HttpResponse
# Create your views here.

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
@permission_classes((AllowAny, ))
class CreateContact(generics.ListCreateAPIView):

    def create(self,request):

        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        queryset = Contact.objects.all()
        serializer = ContactSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)
