from django.shortcuts import render,redirect,HttpResponse
from django import forms
from django.forms import widgets
from blog import models
from django.core.exceptions import ValidationError

class RegForm(forms.Form):
    username = forms.CharField(
        max_length=24,
        label='用户名',
        widget=widgets.TextInput(attrs={"class":"form-control"}),
        error_messages={
            'max_length':'用户名不能大于24位',
            'required':'用户名不能为空',
        }

    )

    password = forms.CharField(
        max_length=6,
        label='密码',
        widget=widgets.PasswordInput(attrs={"class":"form-control"}),
        error_messages={
            'min_length':'密码至少六位',
            'required':'密码不能为空',
        }
    )

    re_password = forms.CharField(
        max_length=6,
        label='确认密码',
        widget=widgets.PasswordInput(attrs={"class":"form-control"}),
        error_messages={
            'min_length': '密码至少六位',
            'required': '密码不能为空',
        }
    )

    email = forms.EmailField(
        label='邮箱',
        widget=widgets.EmailInput(attrs={"class":"form-control"}),
        error_messages = {
            'invalid':'邮箱格式不正确',
            'required': '邮箱不能为空',
        }
    )
    # 用内置form判断用户名邮箱是否存在
    #重写username钩子函数，判断用户名是否注册
    # def clean_username(self):
    #     username = self.cleaned_data.get("username")
    #     user_exist = models.UserInfo.objects.filter(username=username).first()
    #     if user_exist:
    #         self.add_error("username",ValidationError("用户名已注册"))
    #     else:
    #         return username
    # 重写email钩子函数，判断邮箱是否注册
    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_exist = models.UserInfo.objects.filter(email=email).first()
        if email_exist:
            self.add_error("email",ValidationError("邮箱已注册"))
        else:
            return email
    # 重写全局的钩子函数,判断输入密码是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password != re_password:
            self.add_error('re_password',ValidationError('密码不一致'))
            raise ValidationError('密码不一致')
        return self.cleaned_data


