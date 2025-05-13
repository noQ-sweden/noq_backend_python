from django.contrib import admin
from django.urls import path, include
from rest_api.api.api import api


urlpatterns = [
    path('', include("backend.urls")),
    path('admin/', admin.site.urls),
    path('api/', api.urls)
]