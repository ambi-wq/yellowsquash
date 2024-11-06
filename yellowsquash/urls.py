"""yellowsquash URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.generics import UpdateAPIView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # admin panels
    path('admin/', admin.site.urls),

    # authentications
    path('api/auth/', include('apps.custom_auth.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    
    # modules
    path('api/user/',include('apps.user.urls')),
    path('api/program/',include('apps.program.urls')),
    path('api/blog/',include('apps.blog.urls')),
    path('api/media/',include('apps.user_media.urls')),
    path('api/dashboard/',include('apps.dashboard.urls')),
    path('api/contact/',include('apps.contact.urls')),
    path('api/webinar/', include('apps.webinar.urls')),
    path('api/group/', include('apps.group.urls')),
    path('api/calendar/',include('apps.calendarapp.urls')),
    path('api/videos/',include('apps.videos.urls')),
    path('api/queries/',include('apps.queries.urls')),
    path('api/healthpedia/',include('apps.healthpedia.urls')),

]

from apps.utility.update_image_url import UpdateImageUrlApiView
#utility pattern
#urlpatterns+=[
    #path('api/update-image-url/',UpdateImageUrlApiView.as_view()),

#]

urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)

