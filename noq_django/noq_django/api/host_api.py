from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError

from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    Available,
    Product,
    BookingStatus,
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

from typing import List, Dict, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "host")) #request defineras vid call, gruppnamnet är statiskt

@router.get("/count_bookings", response=BookingCounterSchema, tags=["host-frontpage"]) 
def count_bookings(request):
    host = Host.objects.get(users=request.user)
    
    pending_count = Booking.objects.filter(product__host=host, status__description='pending').count()
    arrivals_count = Booking.objects.filter(product__host=host, status__description='accepted', start_date=date.today()).count()
    departures_count = Booking.objects.filter(product__host=host, status__description='checked_in', start_date=date.today() - timedelta(days=1)).count()
    current_guests_count = Booking.objects.filter(product__host=host, status__description='checked_in').count()
    
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
def get_pending_bookings(request, limiter: Optional[int] = None): #Limiter example /pending?limiter=10 for 10 results, empty returns all
    host = Host.objects.get(users=request.user)
    bookings = Booking.objects.filter(product__host=host, status__description='pending')
    
    if limiter is not None and limiter > 0:
        return bookings[:limiter]
    
    return bookings

@router.get("/pending/{booking_id}", response=BookingSchema, tags=["host-manage-requests"])
def detailed_pending_booking(request, booking_id: int):
    host = Host.objects.get(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host=host, status__description='pending')

    return booking

@router.patch("/pending/{booking_id}/appoint", response=BookingSchema, tags=["host-manage-requests"])
def appoint_pending_booking(request, booking_id: int):
    host = Host.objects.get(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host=host, status__description='pending')

    try:
        booking.status = BookingStatus.objects.get(id=3)
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")

# Mall för List
@router.get("/hosts", response=List[HostSchema], tags=["Hosts"])
def host_list(request):
    list = Host.objects
    return list
