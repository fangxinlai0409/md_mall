from django.urls import path
from apps.users.views import UsernameCountView
from . import views

urlpatterns = [
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    path('register/', views.RegisterView.as_view() ),
]