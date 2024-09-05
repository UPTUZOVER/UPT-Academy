
from django.urls import path
from api_views.base_views import (  PupilListCreateView,
    PupilRetrieveUpdateDestroyView,

    LoginView)
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('pupils/register/', PupilListCreateView.as_view(), name='pupil-list-create'),
    path('pupils/register/<uuid:pk>/', PupilRetrieveUpdateDestroyView.as_view(), name='pupil-detail'),

    # Custom login view (username yoki email bilan login qilish)
    path('login/', LoginView.as_view(), name='login'),

    # Token yangilash view (JWT access tokenni refresh qilish)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # JWT tokenni tekshirish (access token validligini tekshirish uchun)
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
