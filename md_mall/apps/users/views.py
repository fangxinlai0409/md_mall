import json
import re

from django.contrib.auth.mixins import AccessMixin,LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.carts.utils import merge_cookie_to_redis
from apps.users.models import User
from md_mall import settings
from utils.views import LoginRequiredJSONMixin
from django_redis import get_redis_connection

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
        merge_cookie_to_redis(request, response)
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
        from apps.users.utils import generic_email_verify_token
        token = generic_email_verify_token(request.user.id)

        message = ""
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, settings.EMAIL_VERIFY_URL+'?token=%s'%token, settings.EMAIL_VERIFY_URL+'?token=%s'%token)
        from_email = 'fxfasdf1234@163.com'
        recipient_list=['fxfasdf1234@163.com']
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(subject=subject,message=message,from_email=from_email,
                                recipient_list=recipient_list,html_message=html_message)
        return JsonResponse({'code':0,'errmsg':'ok'})

class EmailVerifyView(View):
    def put(self,request):
        params = request.GET
        token = params.get('token')
        if token is None:
            return JsonResponse({'code':400,'errmsg':'no params'})

        from apps.users.utils import check_verify_token
        user_id = check_verify_token(token)
        if user_id is None:
            return JsonResponse({'code':400,'errmsg':'no params'})
        user = User.objects.get(id=user_id)
        user.email_active = True
        user.save()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


from apps.users.models import Address
class AddressCreateView(LoginRequiredJSONMixin,View):
    def post(self,request):
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        user = request.user
        # verification params
        new_address = Address.objects.create(
            user=user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )
        address = {
            "id": new_address.id,
            "title": new_address.title,
            "receiver": new_address.receiver,
            "province": new_address.province.name,
            "city": new_address.city.name,
            "district": new_address.district.name,
            "place": new_address.place,
            "mobile": new_address.mobile,
            "tel": new_address.tel,
            "email": new_address.email
        }
        return JsonResponse({'code':0,'errmsg':'ok','address':address})



class AddressView(LoginRequiredJSONMixin,View):
    def get(self,request):
        user = request.user
        addresses = Address.objects.filter(user=user,is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        return JsonResponse({'code':0,'errmsg':'ok','addresses':address_list})

from apps.goods.models import SKU
class UserHistoryView(LoginRequiredJSONMixin,View):
    def post(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'no goods'})
        user = request.user
        redis_cli = get_redis_connection('history')
        redis_cli.lrem('history_%s'%user.id,0,sku_id)
        redis_cli.lpush('history_%s'%user.id,sku_id)
        redis_cli.ltrim('history_%s'%user.id,0,4)
        return JsonResponse({'code':0,'errmsg':'ok'})

    def get(self,request):
        redis_cli= get_redis_connection('history')
        ids = redis_cli.lrange('history_%s'%request.user.id,0,4)
        history_list=[]
        for sku_id in ids:
            sku=SKU.objects.get(id=sku_id)
            history_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        return JsonResponse({'code':0,'errmsg':'ok','skus':history_list})



