from django.urls import path
from django.conf.urls import url
from .views import *


urlpatterns = [
    path('', WebinarList.as_view(),name="webinar list"),
    path('get-webinar/', WebinarList.as_view(),name="webinar list"),
    # path('webinar-details/<webinar_id>/', WebinarDetails.as_view(), name='Webinar Details'),
    url(r'^webinar-details/(?P<pk>\d+)/$', WebinarDetails.as_view(), name="Webinar Details"),
    path(r'<id>/', WebinarDetailsBySlug.get_details_by_id, name="Webinar Details By Id"),
    path(r'slug/<slug>/', WebinarDetailsBySlug.get_details_by_slug, name="Webinar Details by Slug"),
    path('subscribe/new/', WebinarSubscribe.as_view(), name='Webinar Subscription'),
    path('get-webinar-categorywise',WebinarCategoryWiseList.as_view(),name="get webinar category wise"),
    path('upcoming-webinar',UpcomingWebinar.as_view(),name="upcoming webinar list"),
    path('get-webinar-details/<id>', GetWebinarDetails.as_view(), name="Get Webinar Details ID"),

    path('add-favourite-webinar/<webinar_id>',FavouriteWebinar.as_view(),name="add favourite webinar"),
    path('remove-favourite-webinar/<webinar_id>',FavouriteWebinar.as_view(),name="remove favourite webinar"),
    path('favourite-webinar-list',FavouriteWebinarList.as_view(),name="favourite webinar list"),
    path('webinar-list',WebinarListingAPI.as_view(),name="new webinar listing api with category and search filter"),

]
