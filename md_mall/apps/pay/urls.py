from django.urls import path
from . import views

urlpatterns = [
    path('payment/<order_id>/',views.PayUrlView.as_view()),
    path('/payment/status/',views.PaymentStatusView.as_view()),
]