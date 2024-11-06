from django.urls import path
from .views import *

urlpatterns = [
    path('video-tag-list', TagList.as_view(), name="video tag list"),
    path('create-video', CreateVideo.as_view(), name="create video"),
    path('get-video', CreateVideo.as_view(), name="get video"),
    path('update-video/<video_id>', CreateVideo.as_view(), name="update video"),
    path('delete-video/<video_id>', CreateVideo.as_view(), name="delete video"),
    path('update-video-status', VideoStatusUpdate.as_view(), name="update-video-status"),
    path('add-favourite-video/<video_id>', FavouriteVideo.as_view(), name="add favourite video"),
    path('remove-favourite-video/<video_id>', FavouriteVideo.as_view(), name="remove favourite video"),
    path('favourite-video-list',FavouriteVideoList.as_view(),name="favourite video list"),
]
