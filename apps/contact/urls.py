from django.urls import path
from django.conf.urls import url
from .views import CreateContact


urlpatterns = [
    path('create-contact-us/',CreateContact.as_view(),name="contact us info create"),
    path('get-contact-us',CreateContact.as_view(),name="get all contact us info"),
]
