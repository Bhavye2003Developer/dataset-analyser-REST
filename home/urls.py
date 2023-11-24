from django.urls import path
from .views import *

urlpatterns = [
    path("analyse/", home, name="home")
]