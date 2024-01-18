from django.urls import path

# from views import book_room_view

from . import views

# 1. urlpatterns nedan
# 2. views.py   view
#    - select ur databasen
# 3. tables.py
# 4. html-template

urlpatterns = [
    path("", views.index_view, name="index_view"),
    path(
        "available/", views.available_list, name="available_list"
    ),  # Listan som svar på sök
    path("book/", views.reservation_view, name="reservation_view"),
    path("book/<int:host_id>/", views.book_room_view, name="book_room_view"),
]
