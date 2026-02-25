import logging #日志模块

from django.core.paginator import Paginator #分页器
from django.db.models import Q #Q对象，用于复杂查询
from django.http import JsonResponse #json响应
from django.shortcuts import render, redirect, get_object_or_404 #Django视图快捷方式，shortcuts意思为捷径
from django.urls import reverse #URL反向解析
from django.contrib.auth.decorators import login_required #登录装饰器
from django.urls import reverse_lazy #URL反向解析，延迟加载
from django.views.decorators.http import require_http_methods, require_POST, require_GET #HTTP方法限制装饰器

from .forms import PubBlogForm #表单相关
from .models import BlogCategory, Blog, BlogComment #模型相关

logger = logging.getLogger(__name__) # 创建日志记录器

BLOGS_PER_PAGE = 6 # 每页显示的博客数量


# / 首页
def index(request):
    # 查询所有博客（预加载作者和分类）
    # 创建分页器，每页6条
    # 获取当前页码
    # 返回模板和数据
    blogs_qs = Blog.objects.select_related('author', 'category').all() # SQL联表查询，返回所有博客对象
    paginator = Paginator(blogs_qs, BLOGS_PER_PAGE) #创建分页器
    page_number = request.GET.get('page', 1) # 获取当前页码，默认为第1页
    page_obj = paginator.get_page(page_number) # 获取分页对象
    # 返回渲染后的HTML页面，包含分页对象和博客对象列表
    return render(request, 'index.html', context={'page_obj': page_obj, 'blogs': page_obj})


# /blog/detail/<int:blog_id> 博客详情页
def blog_detail(request, blog_id):
    """博客详情页 - 展示文章内容和评论"""
    blog = get_object_or_404( #根据ID获取博客（不存在返回404）
        Blog.objects.select_related('author', 'category'), # # 预加载避免N+1查询
        pk=blog_id #查询条件
    )
    blog.view_count += 1 # 增加阅读次数
    Blog.objects.filter(pk=blog_id).update(view_count=blog.view_count) # 原子更新操作，直接在数据库中执行UPDATE语句
    return render(request, 'blog_detail.html', context={'blog': blog})


# /blog/pub 发布博客页
@require_http_methods(['GET', 'POST'])
@login_required(login_url=reverse_lazy('xhc_auth:login')) # 确保只有已登录用户才能访问改视图，reverse_lazy延迟解析（需要时才转换URL）
def pub(request):
    """发布博客"""
    if request.method == 'GET':
        categories = BlogCategory.objects.all() # 获取所有分类
        return render(request, 'pub.html', context={'categories': categories})
    # 表单验证
    form = PubBlogForm(request.POST)
    if not form.is_valid():
        return JsonResponse({
            "code": "500",
            "msg": "博客发布失败，表单验证失败",
            "errors": dict(form.errors)
        })
    # 获取表单数据
    title = form.cleaned_data.get('title')
    content = form.cleaned_data.get('content')
    category_id = form.cleaned_data.get('category')
    # 获取分类对象
    try:
        category_obj = BlogCategory.objects.get(id=category_id)
    except BlogCategory.DoesNotExist:
        return JsonResponse({
            "code": "500",
            "msg": f"选择的分类(ID:{category_id})不存在"
        })
    # 创建博客对象
    blog = Blog.objects.create(
        title=title,
        content=content,
        category=category_obj,
        author=request.user,
    )
    logger.info("博客创建成功: id=%s, title=%s", blog.id, title)

    return JsonResponse({
        "code": "200",
        "msg": "博客发布成功",
        "data": {"blog_id": blog.id}
    })

# /blog/comment 发表评论
@require_POST
@login_required(login_url=reverse_lazy('xhc_auth:login'))
def pub_comment(request):
    """发表评论"""
    blog_id = request.POST.get('blog_id')
    content = request.POST.get('content')
    if not content or not content.strip(): #确保用户确实输入了有意义的评论内容,假如输入为空
        return redirect(reverse('xhc_blog:blog_detail', kwargs={'blog_id': blog_id})) # 评论无效，不保存直接返回
    # 有内容
    BlogComment.objects.create(content=content, blog_id=blog_id, author=request.user) # 创建评论对象
    return redirect(reverse('xhc_blog:blog_detail', kwargs={'blog_id': blog_id})) # 重定向到博客详情页


# /blog/search 搜索博客
@require_GET
def search(request):
    """搜索博客"""
    q = request.GET.get('q', '').strip() # 获取搜索关键字，并去除首尾空格

    if not q: #如果q是空字符串或None
        blogs_qs = Blog.objects.select_related('author', 'category').all()#返回所有博客（按正常列表显示）
    else: #否则，根据关键字搜索博客
        blogs_qs = Blog.objects.select_related('author', 'category').filter(
            Q(title__icontains=q) | Q(content__icontains=q) # 标题或内容包含关键字，不区分大小写
        )

    paginator = Paginator(blogs_qs, BLOGS_PER_PAGE) # 创建分页器
    page_number = request.GET.get('page', 1) # 获取当前页码，默认为第1页
    page_obj = paginator.get_page(page_number) # 获取分页对象
    return render(request, 'index.html', context={
        'page_obj': page_obj,
        'blogs': page_obj,
        'search_query': q,
    })
