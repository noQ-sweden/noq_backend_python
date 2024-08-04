from .api import api
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include("backend.urls")),
    path('admin/', admin.site.urls),
    path('api/', api.api.urls),
]