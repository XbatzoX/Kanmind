from django.urls import path
from .views import RegistrationView, CustomerLoginView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomerLoginView.as_view(), name='login'),
]
