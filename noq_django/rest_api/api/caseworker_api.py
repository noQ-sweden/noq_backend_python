from django.db.models import Q
from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from datetime import datetime, timedelta

from backend.models import (
    Client,
    Booking,
)

from .api_schemas import (
    StatusSchema,
    UserSchema,
    HostSchema,
    ProductSchema,
    BookingSchema,
    UserShelterStayCountResponse,
)

from backend.auth import group_auth

from typing import List, Dict, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "caseworker"))

# api/caseworker/ returns the host information
@router.get("/", response=str, tags=["caseworker-frontpage"])
def get_caseworker_data(request):
    try:
        return HttpResponse("Caseworker frontpage data comes here...", status=200)
    except Exception as e:
        raise HttpError(500, f"An error occurred: {str(e)}")

@router.get("/user_shelter_stay_count/", response=UserShelterStayCountResponse, tags=["caseworker-frontpage"])
def user_shelter_stay_count(request, user_id: int):
    selected_user = get_object_or_404(Client, id=user_id)
    bookings = Booking.objects.filter(user=selected_user).select_related('product', 'product__host')
    total_nights = sum((booking.end_date - booking.start_date).days for booking in bookings)

    booking_list = [
        BookingSchema(
            id=booking.id,
            status=StatusSchema(value=booking.status), 
            start_date=booking.start_date.isoformat(),
            end_date=booking.end_date.isoformat(),
            product=ProductSchema(
                id=booking.product.id,
                name=booking.product.name,  
                host=HostSchema(
                    id=booking.product.host.id,
                    name=booking.product.host.name
                )
            ),
            user=UserSchema(
                id=booking.user.id,
                name=booking.user.name 
            ),
            shelter_name=booking.product.host.name
        )
        for booking in bookings
    ]

    return {
        "user_id": user_id,
        "total_nights": total_nights,
        "bookings": booking_list
    }
