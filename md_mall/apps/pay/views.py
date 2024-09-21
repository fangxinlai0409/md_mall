from alipay import AliPay, AliPayConfig
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.order.models import OrderInfo
from apps.pay.models import Payment
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

class PaymentStatusView(View):
    """保存订单支付结果"""

    def put(self, request):
        # 获取前端传入的请求参数
        query_dict = request.GET
        data = query_dict.dict()
        # 获取并从请求参数中剔除signature
        signature = data.pop('sign')
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 创建支付宝支付对象
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
        # 校验这个重定向是否是alipay重定向过来的
        success = alipay.verify(data, signature)
        if success:
            # 读取order_id
            order_id = data.get('out_trade_no')
            # 读取支付宝流水号
            trade_id = data.get('trade_no')
            # 保存Payment模型类数据
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )

            # 修改订单状态为待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"])

            # 响应trade_id
            return JsonResponse({'code': 0, 'errmsg': 'OK', 'trade_id': trade_id})
        else:
            # 订单支付失败，重定向到我的订单
            return JsonResponse({'code': 400, 'errmsg': '非法请求'})