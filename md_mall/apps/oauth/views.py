from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from md_mall import settings

class QQLoginURLView(View):
    def get(self, request):
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state='xxxsssxx')
        qq_login_url = qq.get_qq_url()
        return JsonResponse({'code': 0 ,'errmsg': 'ok','login_url': qq_login_url})