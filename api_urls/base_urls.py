from django.urls import path
from api_views.base_views import PupilRegisterView, LoginView

urlpatterns = [
    path('pupil/register/', PupilRegisterView.as_view(), name='pupil-register'),
    path('pupil/login/', LoginView.as_view(), name='login'),
]
