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
        sms_code = '%06d'%randint(0,999999)
        redis_cli.setex(mobile, 300, sms_code)
        print(mobile, sms_code)
        CCP().send_template_sms(mobile,[sms_code, 5], 1)
        return JsonResponse({'code':0,'errmsg':'ok'})
