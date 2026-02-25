from django.urls import path
from . import views

app_name = 'xhc_blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/detail/<int:blog_id>', views.blog_detail, name='blog_detail'),#博客详情页
    path('pub/', views.pub, name='pub'),#发布页
    path('comment/pub', views.pub_comment, name='pub_comment'),#评论发布
    path('search/', views.search, name='search'),#搜索
]