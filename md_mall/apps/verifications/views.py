from random import randint

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP


# Create your views here.
class ImageCodeView(View):
    def get(self, request, uuid):
        from libs.captcha.captcha import captcha
        text, image = captcha.generate_captcha()
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 100, text)
        return HttpResponse(image,content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        if not all([image_code, uuid]):
            return JsonResponse({'code':400,'errmsg':'not enough params'})
        redis_cli = get_redis_connection('code')
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code':400,'errmsg':'code expired'})
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code':400,'errmsg':'code does not match'})
        send_flag = redis_cli.get('send_flag_%s' % mobile)
        print(send_flag)
        if send_flag is not None:

            return JsonResponse({'code':400,'errmsg':'do not send messages frequently'})
        sms_code = '%06d'%randint(0,999999)
        redis_cli.setex(mobile, 300, sms_code)
        redis_cli.setex('send_flag_%s'%mobile, 60,1)

        print(mobile, sms_code)
        CCP().send_template_sms(mobile,[sms_code, 5], 1)


        #sms_code_client = request.POST.get('sms_code')
        # 判断短信验证码是否正确：跟图形验证码的验证一样的逻辑
        # 提取服务端存储的短信验证码：以前怎么存储，现在就怎么提取
        #redis_conn = get_redis_connection('code')
        #sms_code_server = redis_conn.get(mobile)  # sms_code_server是bytes
        # 判断短信验证码是否过期
        #if not sms_code_server:
        #   return JsonResponse({'code': 400, 'errmsg': '短信验证码失效'})
        # 对比用户输入的和服务端存储的短信验证码是否一致
        #if sms_code_client != sms_code_server.decode():
        #   return JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})
        return JsonResponse({'code':0,'errmsg':'ok'})
