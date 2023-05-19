from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from . import views

urlpatterns = [
    path("home/", views.dashboard, name="dashboard"),
]
