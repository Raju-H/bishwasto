from django.urls import path, include
from .views import *

# Add Django site authentication urls (for login, logout, password management)

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/', profile, name='profile'),
]