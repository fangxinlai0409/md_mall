from alipay import AliPay, AliPayConfig
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.order.models import OrderInfo
from utils.views import LoginRequiredJSONMixin
from md_mall import settings
# Create your views here.

class PayUrlView(LoginRequiredJSONMixin,View):
    def get(self,request,order_id):
        try:
            order = OrderInfo.objects.get(order_id = order_id,status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code':200,'errmsg':'no this odder'})
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            config=AliPayConfig(timeout=15),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        pay_url = settings.ALIPAY_URL + "?" + order_string
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'alipay_url': pay_url})