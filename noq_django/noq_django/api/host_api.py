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
    AvailableSchema,
)

from backend.auth import group_auth

from typing import List, Dict
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "host")) #request defineras vid call, gruppnamnet är statiskt

@router.get("/pending_count", tags=["host-frontpage"]) 
def count_pending_bookings(request):
    host = Host.objects.get(users=request.user)
    pending_bookings_count = Booking.objects.filter(product__host=host, status__Description='pending')

    return pending_bookings_count.count()

@router.get("/arrivals_count", tags=["host-frontpage"]) 
def count_arrivals(request):
    host = Host.objects.get(users=request.user)
    arrivals = Booking.objects.filter(product__host=host, status__Description='accepted', start_date=date.today())

    return arrivals.count()

@router.get("/departures_count", tags=["host-frontpage"]) 
def count_departures(request):
    host = Host.objects.get(users=request.user)
    departures = Booking.objects.filter(product__host=host, status__Description='checked_in', start_date=date.today() - timedelta(days=1))

    return departures.count()

@router.get("/current_guests_count", tags=["host-frontpage"]) 
def count_current_guests(request):
    host = Host.objects.get(users=request.user)
    guests = Booking.objects.filter(product__host=host, status__Description='checked_in')

    return guests.count()

@router.get("/available_products", response=Dict[str, int], tags=["host-frontpage"]) 
def count_available_products(request):
    host = Host.objects.get(users=request.user)
    spots = Product.objects.filter(host=host, total_places__gt = 0)
    resp_obj = {}

    for i in spots:
        available = Available.objects.filter(product=i).first()

        if available is None or available.places_left <= 0:
            continue
        if i.type not in resp_obj:
            resp_obj[i.type] = 1
        else:
            resp_obj[i.type] += 1

    return resp_obj

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
