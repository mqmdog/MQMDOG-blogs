from .models import BlogCategory, Blog, BlogComment
from django.contrib import admin


class BlogCategoryAdmin(admin.ModelAdmin):
    list_display =['name']

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'pub_time', 'category', 'author']

class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'pub_time', 'blog', 'author']

admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)