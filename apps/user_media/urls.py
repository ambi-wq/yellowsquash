from django.urls import path
from django.conf.urls import url
from .views import AddMedia, GetMedia, UpdateMedia, GetListStaticResources, \
    GetStaticResources, CreateStaticResources, RetrieveUpdateDestroyStaticResources


urlpatterns = [
    path('<int:media_id>', UpdateMedia.as_view(), name="verify mobile/email"),
    path('upload', AddMedia.as_view(), name="upload media file"),
    path('browse', GetMedia.as_view(), name="get media files"),
    path('add-resource/', CreateStaticResources.as_view(), name="create static resource"),
    path('resource-list/', GetListStaticResources.as_view(), name="get list of static resource"),
    path('get-resource/<slug>', GetStaticResources.as_view(), name="get static resource"),
    path('static-resource/<int:pk>', RetrieveUpdateDestroyStaticResources.as_view(), name="retrieve update destroy with url param  static_resource_id"),
]
