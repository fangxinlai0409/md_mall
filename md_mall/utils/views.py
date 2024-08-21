#class LoginRequiredMixin(AccessMixin):
#    """Verify that the current user is authenticated."""
#
#    def dispatch(self, request, *args, **kwargs):
#       if not request.user.is_authenticated:
#           return JsonResponse({'code': 400, 'errmsg': 'not logged in!'})
#        return super().dispatch(request, *args, **kwargs)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': 'not logged in!'})