from django.db import models

# Create your models here.
from utils.models import BaseModel

class OAuthQQUser(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,verbose_name='user')
    openid = models.CharField(max_length=64, verbose_name='openid',db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'qqlogin user data'
        verbose_name_plural = verbose_name