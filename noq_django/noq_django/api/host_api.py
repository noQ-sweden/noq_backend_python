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

from typing import List
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "host")) #request defineras vid call, gruppnamnet är statiskt

@router.get("/activerequests", tags=["host-frontpage"]) #Visa mängden aktiva förfrågningar
def get_active_requests_count(request):
    host = Host.objects.get(user=request.user)
    pending_bookings = Booking.objects.filter(product__host=host, status__Description='pending')

    return pending_bookings.count()

@router.get("/{host_id}/pending", response=List[BookingSchema], tags=["host-frontpage"]) # Hämta bokningar som inte är godkända
def get_pending_bookings(request, host_id: int):
    host = Host.objects.get(pk=host_id)
    pending_bookings = Booking.objects.filter(product__host=host, status__Description='pending')

    return pending_bookings

@router.get("/arrivals", tags=["host-frontpage"]) #Visa dagens arrivals
def get_arrivals_count(request):
    host = Host.objects.get(user=request.user)
    arrivals = Booking.objects.filter(product__host=host, status__Description='accepted', start_date=date.today())

    return arrivals.count()

@router.get("/departures", tags=["host-frontpage"]) #Visa dagens departures
def get_departures_count(request):
    host = Host.objects.get(user=request.user)
    departures = Booking.objects.filter(product__host=host, status__Description='checked_in', start_date=date.today() - timedelta(days=1))

    return departures.count()

@router.get("/currentguests", tags=["host-frontpage"]) #Visa incheckade gäster
def get_current_guests_count(request):
    host = Host.objects.get(user=request.user)
    guests = Booking.objects.filter(product__host=host, status__Description='checked_in').count()

    return guests

@router.get("/availableproducts", tags=["host-frontpage"]) #Visa tillgängliga sovplatser uppdelat i typ 
def get_available_products(request):
    host = Host.objects.get(user=request.user)
    spots = Product.objects.filter(host=host, total_places__gt = 0)
    resp_obj = {}

    for i in spots: #tack tess :)
        available = Available.objects.filter(product=i).first()

        if available is None or available.places_left <= 0:
            continue
        if i.type not in resp_obj:
            resp_obj[i.type] = 1
        resp_obj[i.type] += 1


    return resp_obj

# Mall för List
@router.get("/hosts", response=List[HostSchema], tags=["Hosts"])
def host_list(request):
    list = Host.objects
    return list


