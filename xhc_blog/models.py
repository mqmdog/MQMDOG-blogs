from django.db import models # 引入Django的模型类
from django.contrib.auth import get_user_model # 引入Django的用户模型

User = get_user_model()

# 博客分类
class BlogCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='分类名称') # 分类名称

    def __str__(self): #__str__ 方法定义对象的字符串表示形式
        return self.name

    #为模型提供额外的配置信息
    class Meta:
        verbose_name = '分类' #设置模型在Django管理后台显示的单数名称
        verbose_name_plural = verbose_name #复数形式的模型名称，通常与单数相同


# 博客
class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, verbose_name='分类')#ForeignKey：外键字段，建立一对多关
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览量')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name
        ordering = ['-pub_time'] #-pub_time 表示按发布时间降序排列（最新的在前）

# 评论
class BlogComment(models.Model):
    content = models.TextField(verbose_name='评论内容')
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments',verbose_name='所属博客')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-pub_time']