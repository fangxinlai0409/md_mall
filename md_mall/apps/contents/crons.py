import time
from utils.goods import get_categories
from apps.contents.models import ContentCategory
def generic_meiduo_index():
    print('----------%s-----------'%time.ctime())
    categories = get_categories()
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    context = {
        'categories': categories,
        'contents': contents
    }
    from django.template import loader
    index_template = loader.get_template('index.html')
    index_html_data = index_template.render(context)
    from md_mall import settings

    file_path = os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/index.html')

    with open(file_path,'w',encoding='utf-8') as f:
        f.write(index_html_data)


