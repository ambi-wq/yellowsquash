from django.urls import path
from django.conf.urls import url
from .views import *


urlpatterns = [
    path('blog-count/', BlogCount.as_view(), name="blog count"),
    path('patient_dashboard',PatientDashboard.as_view(),name='patient dashboard'),
    path('symptoms',SymptomsList.as_view(),name="symptoms list"),
]
