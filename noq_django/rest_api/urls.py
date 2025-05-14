from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_api.api.api import api
from django.conf.urls.static import static


urlpatterns = [
    path('', include("backend.urls")),
    path('admin/', admin.site.urls),
    path('api/', api.urls)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)