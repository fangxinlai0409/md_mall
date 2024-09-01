# Create your views here.
import os.path

from django.shortcuts import render
from django.views import View
from utils.goods import get_categories,get_breadcrumb
from apps.contents.models import ContentCategory
from django.http import JsonResponse
class IndexView(View):
    def get(self,request):
        categories = get_categories()
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set .filter(status=True).order_by('sequence')
        context = {
            'categories':categories,
            'contents':contents
        }
        return render(request,'index.html',context)

from apps.goods.models import GoodsCategory,SKU
class ListView(View):
    def get(self,request,category_id):
        ordering = request.GET.get('ordering')
        page_size = request.GET.get('page_size')
        page = request.GET.get('page')
        try:
            category = GoodsCategory.objects.get(id = category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'no params'})
        breadcrumb=get_breadcrumb(category)
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        from django.core.paginator import Paginator
        paginator = Paginator(skus,per_page=page_size)
        page_skus = paginator.page(page)
        sku_list = []
        for sku in page_skus.object_list:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
        print(sku_list)
        total_num = paginator.num_pages
        return JsonResponse({'code':0,'errmsg':'ok','list':sku_list,'count':total_num,'breadcrumb':breadcrumb})

from haystack.views import SearchView
class SKUSearchView(SearchView):

    def create_response(self):
        # 获取搜索结果
        context = self.get_context()
        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })
        return JsonResponse(sku_list,safe=False)

from utils.goods import get_categories,get_breadcrumb,get_goods_specs
class DetailView(View):
    def get(self,request,sku_id):
        try:
            sku = SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            pass
        categories = get_categories()
        breadcrumb = get_breadcrumb(sku.category)
        goods_specs = get_goods_specs(sku)
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request,'detail.html',context)






