import pickle
import base64

from django_redis import get_redis_connection


def merge_cookie_to_redis(request,response):
    cookie_carts = request.COOKIES.get('carts')
    if cookie_carts is not None:
        carts = pickle.loads(base64.b64decode(cookie_carts))
        cookie_dict = {}
        selected_ids = []
        unselected_ids = []
        for sku_id,count_selected_dicts in carts.items():
            cookie_dict[sku_id] = count_selected_dicts['count']
            if count_selected_dicts['selected']:
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)

        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        pipeline.hmset('carts_%s'%request.user.id,cookie_dict)
        if len(selected_ids)>0:
            user=request.user
            pipeline.sadd('selected_%s'%user.id,*selected_ids)
        if len(unselected_ids)>0:
            pipeline.srem('selected_%s'%user.id,*unselected_ids)

        pipeline.execute()
        response.delete_cookie('cart')