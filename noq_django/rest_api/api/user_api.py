from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from django.db import models
from django.utils import timezone
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
    ProductSchemaWithPlacesLeft,
    AvailableHostProductsSchema,
    ProductSchemaWithDates,
    AvailableDateSchema,
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

    # List of unavailable products
    unavailable_products = Available.objects.filter(available_date=selected_date, places_left=0)

    # Get available products
    available_products_list = Product.objects.exclude(id__in=unavailable_products.values('product_id'))

    hostproduct_dict = {}

    for product in available_products_list: #create dict of available products sorted by host
        available = Available.objects.filter(available_date=selected_date, product=product)
        places_left = available.first().places_left if available.exists() else product.total_places
        product.places_left = places_left
        if product.host in hostproduct_dict:
            hostproduct_dict[product.host].append(product)
        else:
            hostproduct_dict[product.host] = [product]

    return [{"host": host, "products": products} for host, products in hostproduct_dict.items()]

@router.get("/available_host/{host_id}", response=List[AvailableHostProductsSchema], tags=["user-booking"])
def list_available_by_host(request, host_id: int):
    """
    Get all available products for a given host along with the dates they are available.
    'places_left' represents how many entries exist for today only.
    """
    host = get_object_or_404(Host, id=host_id)
    today = date.today()

    available_entries = Available.objects.filter(product__host_id=host_id).select_related("product")

    if not available_entries.exists():
        raise HttpError(404, "No available products found for this host.")

    product_dict = {}
    today_count = {}

    for entry in available_entries:
        product = entry.product

        # Count how many times this product is available today
        if entry.available_date == today:
            today_count[product.id] = today_count.get(product.id, 0) + 1

        if product.id not in product_dict:
            product_dict[product.id] = ProductSchemaWithDates(
                id=product.id,
                name=product.name,
                description=product.description,
                total_places=product.total_places,
                places_left=0,
                host=HostSchema.from_orm(product.host),
                type=product.type,
                available_dates=[]
            )

        product_dict[product.id].available_dates.append(
            AvailableDateSchema(available_date=entry.available_date)
        )

    # Set places_left to just today's count
    for product_id, product_data in product_dict.items():
        product_data.places_left = today_count.get(product_id, 0)

    return [{"host": HostSchema.from_orm(host), "products": list(product_dict.values())}]



@router.post("/request_booking", response=BookingSchema, tags=["user-booking"])
def request_booking(request, booking_data: BookingPostSchema):
    
    try:
        product = Product.objects.get(id=booking_data.product_id)
        
        if not product.bookable:
            raise HttpError(422, "This product is not bookable.")
    
        Available.objects.filter(product=product)
    except Available.DoesNotExist:
        raise HttpError(404, "Product is not available")
    except Product.DoesNotExist:
        raise HttpError(404, "Product does not exist")

    user = Client.objects.get(user=request.user)
    booking = Booking()
    booking.start_date = booking_data.start_date
    booking.end_date = booking_data.end_date
    booking.product = product
    booking.user = user
    booking.status = BookingStatus.objects.get(description="pending")
    try:
        booking.save()
    except Exception as e:
        if e.code == "full":
            raise HttpError(200, json.dumps(e.params))

    return booking


def getBookings (user):
    client = Client.objects.get(user=user)
    status_list = ['completed', 'checked_in']
    # List of bookings for the user
    bookings = (Booking.objects.filter(
        user=client
    ).exclude(
        end_date__lt=timezone.now().date()
    ).exclude(
        status__description__in=status_list
    ).order_by('start_date'))

    return bookings

@router.get("/bookings", response=List[BookingSchema], tags=["user-booking"])
def list_bookings(request):

    return getBookings(request.user)


@router.get("/bookings/confirm/{booking_id}", response=List[BookingSchema], tags=["user-booking"])
def confirm_booking(request, booking_id: int):
    try:
        # Get the booking object, raise an exception if it doesn't exist
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise HttpError(404, "Booking not found.")

    # Ensure that the current user is the owner of the booking
    user = Client.objects.get(user=request.user)
    if booking.user != user:
        raise HttpError(403, "You are not authorized to confirm this booking.")

    try:
        booking.status = BookingStatus.objects.get(description='confirmed')
        booking.save()
        return getBookings(request.user)
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Not able to confirm booking.")


@router.delete("/bookings/{booking_id}", response={200: str, 404: str}, tags=["user-booking"])
def delete_booking(request, booking_id: int):
    try:
        # Get the booking object, raise an exception if it doesn't exist
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise HttpError(404, "Booking not found.")
    
    # Ensure that the current user is the owner of the booking
    user = Client.objects.get(user=request.user)
    if booking.user != user:
        raise HttpError(403, "You are not authorized to delete this booking.")
    
    # Delete the booking
    booking.delete()
    
    # Return a success message
    return 200, "Booking deleted successfully."


