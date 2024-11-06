from django.urls import path
from .views import *

urlpatterns = [
    path('user-query',UserQueries.as_view(),name="user add query"),
    path('user-query/<query_id>',UserQueries.as_view(),name="user edit/delete query"),
    path('expert-query/<comment_id>',ExpertQueries.as_view(),name="expert delete query comment"),
    path('expert-query',ExpertQueries.as_view(),name="expert add comment"),
    path('add-reply',CommentReply.as_view(),name="add reply to comments"),
    path('delete-reply/<reply_id>',CommentReply.as_view(),name="delete reply"),
    path('all-queries',AllQueries.as_view(),name="all queries"),
    path('unanswered-queries',UnansweredQueries.as_view(),name="unanwered_queries"),
    path('query-details/<query_id>',QueryDetails.as_view(),name='query-details'),
    path('comment-like/<comment_id>',QueryCommentLiked.as_view(),name='add or remove like on comment'),


]