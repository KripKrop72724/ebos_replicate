from django.contrib import admin
from django.urls import include, path

from .views.v15_extract_data import extractdata, fileuploaded

urlpatterns = [
    path("", extractdata, name="extractdata"),
    path("fileuploaded", fileuploaded, name="fileuploaded"),
]
