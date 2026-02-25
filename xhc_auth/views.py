import logging
import random
import string
from django.contrib.auth import get_user_model, login, logout #Djiango认证相关
from django.core.mail import send_mail #Django邮件相关
from django.http import JsonResponse #json响应
from django.shortcuts import render, redirect #Django视图快捷方式，shortcuts意思为捷径
from django.views.decorators.http import require_http_methods, require_GET #HTTP方法限制

from .forms import RegisterForm, LoginForm #表单相关
from .models import CaptchaModel #验证码模型

User = get_user_model() # 动态获取当前使用的用户模型
logger = logging.getLogger(__name__) # 创建日志记录器


@require_http_methods(['GET', 'POST'])  #限制允许的HTTP方法

#/auth/login
def xhc_login(request):
    """用户登录视图"""
    # GET请求，渲染登录页面
    if request.method == 'GET':
        return render(request, 'login.html') #render渲染登录页面

    # POST请求，处理登录逻辑
    # 表单是用来确保用户提交的数据符合预期规则，将用户输入的原始数据转换为Python可用的格式
    form = LoginForm(request.POST)  #创建表单实例
    #效果为：数据有问题，让用户重新填写，并告诉他哪里错了
    if not form.is_valid(): # 如果表单数据无效
        return render(request, 'login.html', {'form': form})# 返回带错误信息的表单
    # 获取表单数据，cleaned_data是表单实例的属性，包含所有字段的验证后数据
    email = form.cleaned_data.get('email')  # 获取邮箱字段的值
    password = form.cleaned_data.get('password')  # 获取密码字段的值
    remember = form.cleaned_data.get('remember')  # 获取记住我字段的值
    #用户验证
    user = User.objects.filter(email=email).first()#获取符合邮箱的第一个用户
    if user and user.check_password(password): # 验证用户密码
        login(request, user) # 登录用户
        if not remember: # 如果没有记住我，则设置会话过期时间为0
            request.session.set_expiry(0) # 关闭浏览器即过期
        return redirect('/') # 登录成功，跳转到首页
    # 上面没return，说明用户验证失败
    form.add_error('email', '邮箱或密码错误！')# 添加错误信息
    return render(request, 'login.html', {'form': form})# 返回带错误信息的表单


# /auth/logout
def xhc_logout(request):
    """用户登出视图"""
    logout(request) # 登出用户
    return redirect('/') # 登出成功，跳转到首页


# /auth/register
@require_http_methods(['GET', 'POST'])
def register(request):
    """用户注册视图"""
    if request.method == 'GET':
        return render(request, 'register.html')

    form = RegisterForm(request.POST)
    if form.is_valid(): # 如果表单数据有效
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        User.objects.create_user(email=email, username=username, password=password) # 创建用户
        return redirect('xhc_auth:login') # 注册成功，跳转到登录页面

    return render(request, 'register.html', {'form': form})

# /auth/captcha
@require_GET # 仅允许get请求
def send_email_captcha(request):
    """发送邮箱验证码"""
    email = request.GET.get('email')# 获取邮箱参数
    if not email: # 如果邮箱为空
        return JsonResponse({"code": 400, "message": "邮箱不能为空"})

    # 生成4位随机验证码
    # string.digits这是一个字符串常量，包含所有十进制数字
    # random.sample(population, k)从population中随机获取k个元素
    # "".join(...)将列表中的元素连接成一个字符串,"" 表示使用空字符串作为连接符（即直接拼接，不加任何分隔符）
    captcha = "".join(random.sample(string.digits, 4))
    logger.info("验证码已生成: email=%s, captcha=%s", email, captcha)# 日志记录验证码已生成

    # 更新或创建验证码记录
    CaptchaModel.objects.update_or_create(
        email=email,
        defaults={"captcha": captcha} # 如果存在则更新，否则创建
    )

    #发送邮件
    try:
        send_mail(
            subject="XHC博客注册验证码",
            message=f"您的注册验证码是：{captcha}，请勿泄露给他人。",
            recipient_list=[email], # 收件人列表
            from_email=None, # 使用settings中配置的默认发件人
        )
    except Exception as e:
        # 异常处理
        logger.error("邮件发送失败: %s", e)
        return JsonResponse({"code": 500, "message": "邮件发送失败，请稍后重试"})
    #成功响应
    return JsonResponse({"code": 200, "message": "邮箱验证码发送成功！"})
