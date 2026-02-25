from django import forms
from django.contrib.auth import get_user_model
from .models import CaptchaModel

User = get_user_model()# 获取当前使用的用户模型

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=2, error_messages={
        'required': '请输入用户名！',
        "max_length": '用户名长度在2~20之间！',
        "min_length": '用户名长度在2~20之间！'
    })
    email = forms.EmailField(error_messages={'required': '请输入邮箱！', 'invalid': '请传入一个正确的邮箱！'})
    captcha = forms.CharField(max_length=4, min_length=4)
    password = forms.CharField(max_length=20, min_length=6)

    def clean_email(self): #自定义验证方法
        email = self.cleaned_data.get('email') #  获取邮箱值
        exists = User.objects.filter(email=email).exists() # 判断邮箱是否已经存在
        if exists:
            raise forms.ValidationError('邮箱已经被注册！') #抛出验证错误
        return email #返回验证后的邮箱值

    def clean_captcha(self): # 自定义验证方法
        captcha = self.cleaned_data.get('captcha')
        email = self.cleaned_data.get('email')
        # 查询验证码是否存在且匹配
        captcha_model = CaptchaModel.objects.filter(email=email, captcha=captcha).first()
        if not captcha_model:
            raise forms.ValidationError("验证码和邮箱不匹配！")
        captcha_model.delete() # 删除验证码
        return captcha #返回验证后的验证码值

class LoginForm(forms.Form): # 登录表单
    email = forms.EmailField(error_messages={'required': '请输入邮箱', 'invalid': '请传入一个正确的邮箱'})
    password = forms.CharField(max_length=20, min_length=4)
    remember = forms.IntegerField(required=False)