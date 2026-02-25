from django.urls import path
from .import views
app_name='xhc_auth'#应用命名空间
urlpatterns = [
    path('login', views.xhc_login, name='login'),#登录
    path('logout', views.xhc_logout, name='logout'),#登出
    path('register', views.register, name='register'),#注册
    path('captcha', views.send_email_captcha, name='send_email_captcha'),#邮箱验证码
]