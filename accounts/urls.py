from django.contrib.auth.views import LoginView
from django.urls import path
from .views import RegisterView, CustomLoginView, custom_logout_view, settings_view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('logout/', custom_logout_view, name='logout'),
    path("settings/", settings_view, name="settings"),
]
