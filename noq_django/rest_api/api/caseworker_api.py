from django.db.models import Q
from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from django.http import JsonResponse
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
    BookingPerNightSchema,
    UserShelterStayCountSchema,
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
)

from backend.auth import group_auth

from typing import List, Dict, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
router = Router(auth=lambda request: group_auth(request, "caseworker"))  # request defineras vid call, gruppnamnet är statiskt

# api/caseworker/ returns the host information
@router.get("/", response=str, tags=["caseworker-frontpage"])
def get_caseworker_data(request):
    try:
        host = Host.objects.get(users=request.user)
        return host
    except:
        raise HttpError(200, "User is not a caseworker.")
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



@router.get("/get_user_shelter_stay_count/", response=UserShelterStayCountSchema, tags=["caseworker-frontpage"])
def get_user_shelter_stay_count(request, user_id: int):
    try:
        selected_user = get_object_or_404(Client, id=user_id)

        user_bookings = Booking.objects.filter(user=selected_user).select_related(
            'product', 'product__host', 'user', 'user__region'
        ).values(
            'id', 'start_date', 'end_date', 
            'product__host__region__name', 
            'product__host__name',          
        )

        total_nights = sum(
            (booking['end_date'] - booking['start_date']).days
            for booking in user_bookings
        )

        booking_list = [
            BookingPerNightSchema(
                id=booking['id'],
                start_date=booking['start_date'].isoformat(),
                end_date=booking['end_date'].isoformat(),
                region=booking['product__host__region__name'],
                shelter_name=booking['product__host__name'], 
            )
            for booking in user_bookings
        ]

        response_data = UserShelterStayCountSchema(
            user_id=user_id,
            total_nights=total_nights,
            bookings=booking_list
        )
        
        return response_data

    except Exception as e:
        return JsonResponse({'detail': f"An error occurred: {str(e)}"}, status=500)
