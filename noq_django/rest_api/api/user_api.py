from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from django.db import models
from django.core.exceptions import ValidationError
from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    BookingStatus,
    Available,
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
    AvailableProductsSchema,
)

from backend.auth import group_auth

from typing import List
import json
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date

router = Router(auth=lambda request: group_auth(request, "user")) #request defineras vid call, gruppnamnet är statiskt

@router.get("/available/{selected_date}", response=List[AvailableProductsSchema], tags=["user-booking"])
def list_available(request, selected_date: str):
    try:
        selected_date = models.DateField().to_python(selected_date)
    except ValueError:
        raise HttpError(404, "Invalid date, dates need to be in the YYYY-MM-DD format")

    available_list = Available.objects.filter(available_date=selected_date) #get all available products

    hostproduct_dict = {}

    for available in available_list: #create dict of available products sorted by host
        if available.product.host in hostproduct_dict:
            product = available.product
            product.places_left = available.places_left
            hostproduct_dict[available.product.host].append(available.product)
        else:
            product = available.product
            product.places_left = available.places_left
            hostproduct_dict[available.product.host] = [available.product]

    
    return [{"host": host, "products": products} for host, products in hostproduct_dict.items()]

@router.post("/booking", response=BookingSchema, tags=["user-booking"])
def create_booking(request, booking_data: BookingPostSchema):
    try:
        product = Product.objects.get(id=booking_data.product_id)
        is_available = Available.objects.filter(product=product, available_date__range=[booking_data.start_date, booking_data.end_date]).exists()
        if not is_available:
            raise Available.DoesNotExist()
    except Product.DoesNotExist:
        raise HttpError(404, "Product does not exist")
    except Available.DoesNotExist:
        raise HttpError(404, "Product is not available for the selected dates")

    user = Client.objects.get(user=request.user)
    booking = Booking(
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        product=product,
        user=user,
        status=BookingStatus.objects.get(description="pending")
    )
    
    try:
        booking.full_clean()
        booking.save()
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        if hasattr(e, 'code') and e.code == "full":
            raise HttpError(409, "This product is fully booked for the selected dates")
        raise HttpError(500, "An unexpected error occurred")

    return booking

@router.post("/request_booking", response=BookingSchema, tags=["user-booking"])
def create_booking(request, booking_data: BookingPostSchema):
    try:
        product = Product.objects.get(id=booking_data.product_id)
        is_available = Available.objects.filter(product=product, available_date__range=[booking_data.start_date, booking_data.end_date]).exists()
        if not is_available:
            raise Available.DoesNotExist()
    except Product.DoesNotExist:
        raise HttpError(404, "Product does not exist")
    except Available.DoesNotExist:
        raise HttpError(404, "Product is not available for the selected dates")

    user = Client.objects.get(user=request.user)
    booking = Booking(
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        product=product,
        user=user,
        status=BookingStatus.objects.get(description="pending")
    )
    
    try:
        booking.full_clean()
        booking.save()
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        if hasattr(e, 'code') and e.code == "full":
            raise HttpError(409, "This product is fully booked for the selected dates")
        raise HttpError(500, "An unexpected error occurred")

    return booking
