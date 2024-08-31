from django.db import models

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='Created at')
    update_time = models.DateTimeField(auto_now=True,verbose_name='Updated at')
    class Meta:
        abstract = True