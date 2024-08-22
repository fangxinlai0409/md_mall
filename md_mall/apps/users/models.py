from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)
    email_active = models.BooleanField(default=False,verbose_name='isvalid email')

    class Meta:
        db_table = 'tb_users'
        verbose_name = 'user manage'
        verbose_name_plural = verbose_name

