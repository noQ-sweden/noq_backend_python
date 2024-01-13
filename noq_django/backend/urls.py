from django.urls import path
# from views import reservation_view

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('book/', views.reservation_view, name='reservation_view'),
]