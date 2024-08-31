from django.core.files.storage import Storage
class MyStorage(Storage):
    pass

    def _open(self,name):
        pass
    def _save(self,name,content,max_length = None):
        pass

    def url(self,name):
        return "http://10.0.2.15:8888/" + name