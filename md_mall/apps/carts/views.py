import json

from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

# Create your views here.
import base64
import pickle
from apps.goods.models import SKU
from django.http import JsonResponse
class CartsView(View):
    def post(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'no goods'})
        try:
            count = int(count)
        except Exception:
            count = 1
        user = request.user
        if user.is_authenticated:
            redis_cli=get_redis_connection('carts')
            redis_cli.hset('carts_%s'%user.id,sku_id,count)
            redis_cli.sadd('selected_%s'%user.id,sku_id)
            return JsonResponse({'code':0,'errmsg':'ok'})
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                carts=pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts={}
            if sku_id in carts:
                origin_count = carts[sku_id]['count']
                count+=origin_count

            carts[sku_id]={
                'count':count,
                'selected':True
            }

            carts_bytes= pickle.dumps(carts)
            base64encode = base64.b64encode(carts_bytes)
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('carts',base64encode.decode(),max_age=3600*24*12)
            return response
    def get(self,request):
        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            sku_id_counts=redis_cli.hgetall('carts_%s'%user.id)
            selected_ids=redis_cli.smembers('selected_%s'%user.id)
            carts={}
            for sku_id,count in sku_id_counts.items():
                carts[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in selected_ids
                }

        else:
            cookie_carts=request.COOKIES.get('carts')
            if cookie_carts is not None:
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}
        sku_ids = carts.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        sku_list=[]
        for sku in skus:
            sku_list.append({
                'id':sku.id,
                'price':sku.price,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'selected':carts[sku.id]['selected'],
                'count':carts[sku.id]['count'],
                'amount':sku.price*carts[sku.id]['count']
            })
        print(sku_list)
        return JsonResponse({'code':0,'errmsg':'ok','cart_skus':sku_list})
