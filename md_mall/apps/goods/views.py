from django.shortcuts import render

# Create your views here.

from fdfs_client.client import Fdfs_client

client = Fdfs_client('/home/fxl/Desktop/meiduoshangcheng/md_mall/md_mall/utils/fastdfs/client.conf')
print(client.upload_by_filename('/home/fxl/Desktop/Untitled.jpeg'))
