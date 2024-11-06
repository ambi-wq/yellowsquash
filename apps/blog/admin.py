from django.contrib import admin
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)
from .models import Tag, Blog, BlogView, BlogLike, BlogComment, BlogShare

admin.site.register(Tag)

class BLogAdmin(admin.ModelAdmin):
    search_fields = ('id', 'title', 'slug')
    list_filter = (
        ('approved_by', RelatedDropdownFilter), 
        ('tags', RelatedDropdownFilter),
        ('categories', RelatedDropdownFilter),
        ('status', ChoiceDropdownFilter),
    )
    list_display = 'id', 'title', 'status', 'slug', 'created_at', 'updated_at'
    ordering = ('-updated_at',)

admin.site.register(Blog, BLogAdmin)


class BlogViewAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'blog__title')
    list_filter = (
        ('blog', RelatedDropdownFilter), 
        ('user', RelatedDropdownFilter),
    )
    list_display = 'user', 'blog', 'created_at'
    ordering = ('-created_at',)

admin.site.register(BlogView, BlogViewAdmin)


class BlogLikeAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'blog__title')
    list_filter = (
        ('blog', RelatedDropdownFilter), 
        ('user', RelatedDropdownFilter),
    )
    list_display = 'user', 'blog', 'created_at'
    ordering = ('-created_at',)

admin.site.register(BlogLike, BlogLikeAdmin)


class BlogCommentAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'blog__title', 'comment')
    list_filter = (
        ('blog', RelatedDropdownFilter), 
        ('user', RelatedDropdownFilter),
    )
    list_display = 'user', 'blog', 'comment', 'created_at'
    ordering = ('-created_at',)
    
admin.site.register(BlogComment, BlogCommentAdmin)

class BlogShareAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'blog__title',)
    list_filter = (
        ('blog', RelatedDropdownFilter), 
        ('user', RelatedDropdownFilter),
    )
    list_display = 'user', 'blog', 'created_at'
    ordering = ('-created_at',)
    
admin.site.register(BlogShare, BlogShareAdmin)

