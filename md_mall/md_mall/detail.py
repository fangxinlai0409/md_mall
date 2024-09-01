import sys
sys.path.insert(0, '../')

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "md_mall.settings")


import django
django.setup()

from utils.goods import get_goods_specs,get_categories,get_breadcrumb
from apps.goods.models import SKU
def generic_detail_html(sku):
    categories = get_categories()
    breadcrumb = get_breadcrumb(sku.category)
    goods_specs = get_goods_specs(sku)
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }
    from django.template import loader
    detail_template = loader.get_template('detail.html')
    detail_html_data = detail_template.render(context)
    import os
    from md_mall import settings
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/goods/%s.html' % sku.id)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_data)


skus = SKU.objects.all()
for sku in skus:
    generic_detail_html(sku)