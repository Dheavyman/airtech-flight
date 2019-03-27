from django.urls import path

from .views import RegisterView, LoginView, ProfilePhotoView

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name='create_account'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('users/<int:pk>/photo', ProfilePhotoView.as_view(), name='profile_photo')
]
