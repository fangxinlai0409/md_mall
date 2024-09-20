import json
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
# Create your views here.
from utils.views import LoginRequiredJSONMixin
from apps.users.models import Address
class OrderSettlementView(LoginRequiredJSONMixin,View):
    def get(self,request):
        user = request.user
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        addresses_list=[]
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })

        redis_cli = get_redis_connection('carts')
        pipeline=redis_cli.pipeline()
        pipeline.hgetall('carts_%s' % user.id)
        pipeline.smembers('selected_%s' % user.id)
        result = pipeline.execute()
        sku_id_counts = result[0]
        print(sku_id_counts)
        selected_ids = result[1]
        print(selected_ids)
        selected_carts = {}
        for sku_id in selected_ids:
            selected_carts[int(sku_id)] = int(sku_id_counts[sku_id])
        sku_list=[]
        for sku_id,count in selected_carts.items():
            sku = SKU.objects.get(pk=sku_id)
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'count': count,
                'price':sku.price
            })
        from decimal import Decimal
        freight = Decimal('10')
        context={
            'skus':sku_list,
            'addresses':addresses_list,
            'freight':freight
        }
        return JsonResponse({'code':0,'errmsg':'ok','context':context})

from apps.order.models import OrderInfo
class OrderCommitView(View):
    def post(self,request):
        user = request.user
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_methond = data.get('pay_method')
        if not all([address_id,pay_methond]):
            return JsonResponse({'code':400,'errmsg':'not enough params'})
        try:
            address = Address.objects.get(id = address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': 'error params'})

        if pay_methond not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': 'error params'})

        from django.utils import timezone
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d'%user.id
        if pay_methond == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        total_count = 0
        total_amount = Decimal('0')
        freight = Decimal('10.00')

        OrderInfo.objects.create(
            order_id = order_id,
            user = user,
            address = address,
            total_count = total_count,
            total_amount = total_amount,
            freight = freight,
            pay_method = pay_methond,
            status=status
        )