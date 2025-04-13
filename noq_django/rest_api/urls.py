from .api import api
from django.contrib import admin
from django.urls import path, include
from backend import views


urlpatterns = [
    path('', include("backend.urls")),
    path('admin/', admin.site.urls),
    path('api/', api.api.urls),
    path('sse/booking_updates/<int:user_id>/', views.sse_booking_updates_view, name='sse_booking_updates'),
]