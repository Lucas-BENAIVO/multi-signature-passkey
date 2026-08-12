from django.urls import path

from accounts.views import LoginView, MeView, RsaPublicKeyView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/rsa-public-key/', RsaPublicKeyView.as_view(), name='auth-rsa-public-key'),
]
