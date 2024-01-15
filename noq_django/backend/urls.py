from django.urls import path

# from views import reservation_view

from . import views

urlpatterns = [
    path("", views.index_view, name="index_view"),
    path("book/", views.reservation_view, name="reservation_view"),
    path("book/<int:host_id>/", views.book_room_view, name="book_room_view"),
]
