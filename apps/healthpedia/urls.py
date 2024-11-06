from django.urls import path
from .views import *

urlpatterns = [
    path('blog-list',BlogList.as_view(),name="blog-list"),
    path('video-list',VideoList.as_view(),name='video-list'),

]