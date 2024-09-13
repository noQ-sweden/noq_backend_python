from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from backend.models import Client, Booking, Host
from .api_schemas import (
    BookingPerNightSchema,
    UserShelterStayCountSchema,
)
from backend.auth import group_auth
from typing import List
from ninja.errors import HttpError

router = Router(auth=lambda request: group_auth(request, "caseworker"))  # request defineras vid call, gruppnamnet är statiskt

# api/caseworker/ returns the host information
@router.get("/", response=str, tags=["caseworker-frontpage"])
def get_caseworker_data(request):
    try:
        host = Host.objects.get(users=request.user)
        return host
    except:
        raise HttpError(200, "User is not a caseworker.")

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
