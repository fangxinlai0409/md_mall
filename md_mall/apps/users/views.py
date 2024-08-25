import json
import re

from django.contrib.auth.mixins import AccessMixin,LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
from utils.views import LoginRequiredJSONMixin


# Create your views here.

# check user duplication
class UsernameCountView(View):

    def get(self, request, username):

        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})

class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


class RegisterView(View):

    def post(self, request):
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)

        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数!'})
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return JsonResponse({'code': 400, 'errmsg': 'username格式有误!'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': 'password格式有误!'})
        # 判断两次密码是否一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次输入不对!'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': 'mobile格式有误!'})
        # 判断是否勾选用户协议
        if allow != True:
            return JsonResponse({'code': 400, 'errmsg': 'allow格式有误!'})

        user=User.objects.create_user(username=username, password=password, mobile=mobile)

        from django.contrib.auth import login
        login(request, user)


        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class LoginView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': 'not enough params!'})
        if re.match(r'^1[3-9]\d{9}$', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD =  'username';
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'code': 400, 'errmsg': 'username or password error!'})
        login(request, user)
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username',username)
        return response

from django.contrib.auth import logout
class LogoutView(View):
    def delete(self, request):
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response



class InfoView(LoginRequiredJSONMixin,View):
    def get(self,request):
        info_data={
            'username':request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok','info_data':info_data})


class EmailView(View):
    def put(self,request):
        data = json.loads(request.body.decode())
        email = data.get('email')
        #verification email

        user = request.user
        user.email=email
        user.save()
        from django.core.mail import send_mail
        subject='md_mall active'
        message = "click to active <a href='http://www.itcast.cn'>active</a>"
        from_email = 'fxfasdf1234@163.com'
        recipient_list=['fxfasdf1234@163.com']
        send_mail(subject=subject,html_message=message,from_email=from_email,recipient_list=recipient_list)
        return JsonResponse({'code':0,'errmsg':'ok'})












