from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_api.api.api import api
from django.contrib import admin

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
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('sleeping_spaces/', views.list_sleeping_spaces, name='list_sleeping_spaces'),
    path('sleeping_spaces/create/', views.create_sleeping_space, name='create_sleeping_space'),
    path('sleeping_spaces/update/<int:pk>/', views.update_sleeping_space, name='update_sleeping_space'),
    path('sleeping_spaces/delete/<int:pk>/', views.delete_sleeping_space, name='delete_sleeping_space'),
    path('bookings/daily/', views.daily_bookings_view, name='daily_bookings_view'),
    path('host/<int:host_id>/', views.host_bookings_view, name='host_bookings'),
    path("resources/", views.resource_list, name="resource_list"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path('api/token/', obtain_auth_token),

]
