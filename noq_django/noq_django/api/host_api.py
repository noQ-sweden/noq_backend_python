from ninja import NinjaAPI, Schema, ModelSchema, Router
from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    Available,
    Product,
)

from .api_schemas import (
    RegionSchema,
    UserSchema,
    UserPostSchema,
    HostSchema,
    HostPostSchema,
    HostPatchSchema,
    ProductSchema,
    BookingSchema,
    BookingPostSchema,
    BookingCounterSchema,
    AvailableSchema,
)

from backend.auth import group_auth

from typing import List, Dict
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "host")) #request defineras vid call, gruppnamnet är statiskt

@router.get("/count_bookings", response=BookingCounterSchema, tags=["host-frontpage"]) 
def count_bookings(request):
    host = Host.objects.get(users=request.user)
    
    pending_count = Booking.objects.filter(product__host=host, status__Description='pending').count()
    arrivals_count = Booking.objects.filter(product__host=host, status__Description='accepted', start_date=date.today()).count()
    departures_count = Booking.objects.filter(product__host=host, status__Description='checked_in', start_date=date.today() - timedelta(days=1)).count()
    current_guests_count = Booking.objects.filter(product__host=host, status__Description='checked_in').count()
    
    spots = Product.objects.filter(host=host, total_places__gt=0)
    available_products = {}
    for i in spots:
        available = Available.objects.filter(product=i).first()
        if available is not None and available.places_left > 0:
            available_products[i.type] = available_products.get(i.type, 0) + 1
    
    return BookingCounterSchema(
        pending_count=pending_count,
        arrivals_count=arrivals_count,
        departures_count=departures_count,
        current_guests_count=current_guests_count,
        available_products=available_products
    )

@router.get("/pending", response=List[BookingSchema], tags=["host-manage-requests"])
def get_pending_bookings(request):
    host = Host.objects.get(users=request.user)
    bookings = Booking.objects.filter(product__host=host)
    
    return bookings 

@router.get("/pending/{booking_id}", response=BookingSchema, tags=["host-manage-requests"])
def detailed_pending_booking(request, booking_id: int):
    host = Host.objects.get(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host=host)

    return booking 
