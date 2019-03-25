from django.urls import path

from .views import RegisterView, LoginView

urlpatterns = [
    path('register', RegisterView.as_view(), name='create_account'),
    path('login', LoginView.as_view(), name='login')
]
