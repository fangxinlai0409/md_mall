from django.urls import path
from apps.users.views import UsernameCountView
from . import views

urlpatterns = [
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view()),
    path('register/', views.RegisterView.as_view() ),
    path('login/', views.LoginView.as_view() ),
    path('logout/', views.LogoutView.as_view() ),
    path('info/', views.InfoView.as_view() ),
    path('emails/', views.EmailView.as_view() ),
    path('emails/verification/', views.EmailVerifyView.as_view() ),
]