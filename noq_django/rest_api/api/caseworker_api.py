from django.db.models import Q
from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from django.db import transaction
from datetime import datetime, timedelta

from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    Available,
    Product,
    BookingStatus,
    State,
    Invoice,
    InvoiceStatus,
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
    AvailablePerDateSchema,
    InvoiceCreateSchema,
    InvoiceResponseSchema,
    BookingUpdateSchema,
    ProductSchemaWithPlacesLeft,
)

from backend.auth import group_auth

from typing import List, Dict, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "caseworker"))  # request defineras vid call, gruppnamnet är statiskt

@router.get("/bookings/pending", response=List[BookingSchema], tags=["caseworker-manage-requests"])
def get_pending_bookings(request, limiter: Optional[int] = None):  # Limiter example /pending?limiter=10 for 10 results, empty returns all
    hosts = Host.objects.filter(users=request.user)
    bookings = []
    for host in hosts:
        host_bookings = Booking.objects.filter(product__host=host, status__description='pending')
        for booking in host_bookings:
            bookings.append(booking)

    if limiter is not None and limiter > 0:
        return bookings[:limiter]

    return bookings


@router.patch("/bookings/batch/accept", response={200: dict, 400: dict}, tags=["caseworker-manage-requests"])
def batch_appoint_pending_booking(request, booking_ids: list[BookingUpdateSchema]):
    hosts = Host.objects.filter(users=request.user)
    # Use a transaction to ensure all or nothing behavior
    with transaction.atomic():
        errors = []
        for item in booking_ids:
            booking_id = item.booking_id
            booking = get_object_or_404(Booking, id=booking_id, product__host__in=hosts, status__description='pending')
            try:
                booking.status = BookingStatus.objects.get(description='accepted')
                booking.save()
            except Exception as e:
                # Collect errors for any failed updates
                errors.append({'booking': item.booking_id, 'error': str(e)})
        if errors:
            return 400, {'message': 'Some updates failed', 'errors': errors}

    return 200, {'message': 'Batch update successful'}


@router.patch("/bookings/{booking_id}/accept", response=BookingSchema, tags=["caseworker-manage-requests"])
def appoint_pending_booking(request, booking_id: int):
    hosts = Host.objects.filter(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host__in=hosts, status__description='pending')

    try:
        booking.status = BookingStatus.objects.get(description='accepted')
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")


@router.patch("/bookings/{booking_id}/decline", response=BookingSchema, tags=["caseworker-manage-requests"])
def decline_pending_booking(request, booking_id: int):
    hosts = Host.objects.filter(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host__in=hosts, status__description='pending')

    try:
        booking.status = BookingStatus.objects.get(description='declined')
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")


# This API can be used to undo previous decision for accept or decline
# Bookings that have status checked_in can't be changed.
@router.patch("/bookings/{booking_id}/setpending", response=BookingSchema, tags=["caseworker-manage-requests"])
def set_booking_pending(request, booking_id: int):
    hosts = Host.objects.filter(users=request.user)
    valid_statuses = ['accepted', 'declined']
    booking = get_object_or_404(Booking, id=booking_id, product__host__in=hosts, status__description__in=valid_statuses)

    try:
        booking.status = BookingStatus.objects.get(description='pending')
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")
    

@router.get("/available_all", response=List[ProductSchemaWithPlacesLeft], tags=["host-available"])
def get_available_places_all(request):
    # Retrieve all hosts the caseworker is responsible for
    hosts = Host.objects.filter(caseworkers=request.user)  # Assuming caseworkers are linked to Hosts via the 'users' relationship
    
    if not hosts.exists():
        # No hosts associated with the caseworker, return a 404 error
        raise HttpError(404, "No hosts associated with this caseworker.")
    
    available_products = []
    
    # Loop through each host and get the products
    for host in hosts:
        products = Product.objects.filter(host=host)
        
        # Loop through each product and check available places
        for product in products:
            # Find availability for the product
            available = Available.objects.filter(product=product).first()
            
            # Calculate the number of places left
            places_left = available.places_left if available else product.total_places
            
            # Append the product with the remaining places to the list
            available_products.append(
                ProductSchemaWithPlacesLeft(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    total_places=product.total_places,
                    host=product.host,  
                    type=product.type,
                    places_left=places_left
                )
            )
    
    # Return the full list of available products across all hosts
    return available_products
