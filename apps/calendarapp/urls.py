from django.urls import path
from .views import *

urlpatterns = [
    path('get-calendar-list',CalendarList.as_view(),name="get-calendar-list")
]