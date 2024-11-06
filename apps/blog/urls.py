from django.urls import path
from .views import *

urlpatterns = [
    path('blog-tag-list', TagsList.as_view(), name="list of blog tags"),
    path('search-blog-list/', SearchBlogList.as_view(), name="list of blogs"),
    path('my-blog-list', MyBlogList.as_view(), name="my blogs"),
    path('expert-blog-list/<int:expert_id>', ExpertBlogList.as_view(), name="list of blogs"),
    path('blog-details/<slug>', BlogDetails.as_view(), name="details blogs"),
    path('blog-view/<slug>/', BlogViewCount.as_view(), name="blogs view"),
    path('blog-comments/<slug>/', BlogCommentsApi.as_view(), name="details comments"),
    path('create-blog', CreateBlogApi.as_view(), name="create blog api"),
    path('update-blog/<int:blog_id>', UpdateBlogApi.as_view(), name="update blog api"),
    path('update-blog-status/<int:blog_id>/<blog_status>', BlogStatusUpdateApi.as_view(),
         name="update blog status to approve/reject/publish/unpublish"),
    path('delete-blog/<int:blog_id>', DeleteBlogApi.as_view(), name="delete blog api"),
    path('add-blog-comment/<int:blog_id>/', AddBlogComment.as_view(), name="add user comment on blog"),
    path('update-blog-comment/<int:blog_comment_id>/', UpdateBlogComment.as_view(), name="update user comment on blog"),
    path('delete-blog-comment/<int:blog_comment_id>/', DeleteBlogComment.as_view(), name="delete user comment on blog"),
    path('blog-like-dislike/<int:blog_id>/', BlogLikeDislike.as_view(), name="user blog like or dislike"),
    path('blog-share/<int:blog_id>/', UserBlogShare.as_view(), name="user shared blog on some platform"),
    path('blog-like-share-view/', BlogLikeShareView.as_view(), name="user like view and share one table"),
    path('get-filter-blog/', GlobalSearchBlog.as_view(), name="global blog search"),

    path('get-blog/<int:blog_id>', GetSingleBlogApi.as_view(), name="get individual blog item"),
    path('add-favourite-blog/<blog_id>',AddFavouriteBlog.as_view(),name="add favourite blog"),
    path('remove-favourite-blog/<blog_id>',AddFavouriteBlog.as_view(),name='remove favourite blog'),
    path('favourite-blog-list',FavouriteBlogList.as_view(),name="favourite blog list"),

]
