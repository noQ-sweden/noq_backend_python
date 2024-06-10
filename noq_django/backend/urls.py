from django.urls import path
from . import views


# from views import book_room_view

# Django documentation

#   1. urlpatterns  nedan
#   2. views.py     view
#
#   3. tables.py
#   4. html-template

urlpatterns = [
    path("", views.main_view, name="main_view"),
    path("search", views.search_view, name="search_view"),
    path(
        "available/", views.available_list, name="available_list"
    ),  # Listan som svar på sök
    # path("book/", views.reservation_view, name="reservation_view"),
    path("book/<int:available_id>/", views.book_room_view, name="book_room_view"),
    path('host/<int:host_id>/bookings/', views.host_bookings_view, name='host_bookings'),
]
