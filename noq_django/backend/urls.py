from django.urls import path
from . import views
from .views import activityes_list, volunteer_activityes_signup, volunteer_activityes_cancel, volunteer_activityes_list

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
    path('api/activities/list', activityes_list, name='activityes-list'),
    path('api/volunteer/activities/signup/<int:activity_id>', volunteer_activityes_signup, name='volunteer-activityes-signup'),
    path('api/volunteer/activities/cancel/<int:activity_id>', volunteer_activityes_cancel, name='volunteer-activityes-cancel'),
    path('api/volunteer/activities/list', volunteer_activityes_list, name='volunteer-activityes-list')
]
