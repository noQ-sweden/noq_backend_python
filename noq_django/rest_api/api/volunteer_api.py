from ninja import Router
from backend.auth import group_auth
from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from django.db import models
from django.utils import timezone
from django.db.models import Q
from typing import List
import json

from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    BookingStatus,
    Available,
    User,
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
    VolunteerBookingPostSchema,
    BookingPostSchema,
    AvailableSchema,
    AvailableProductsSchema,
    ClientSchema,
    VolunteerCreateClientPostSchema,
)

router = Router(auth=lambda request: group_auth(request, "volunteer"))  #request defineras vid call, gruppnamnet är statiskt

@router.get("/clients", tags=["Volunteer"])
def clients(request):
    return {"status": "success"}, 200


@router.get("/available", response=List[AvailableProductsSchema], tags=["Volunteer"]) #response=List[AvailableProductsSchema], tags=["Volunteer"])
def list_available(request):
    try:
        selected_date = models.DateField().to_python(timezone.now())
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


@router.get("/guest/search", response=List[ClientSchema], tags=["Volunteer"])
def search_guest(request):
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    uno_code = request.GET.get('uno', '')

    query = Q()
    if first_name:
        query |= Q(first_name__icontains=first_name)
    if last_name:
        query |= Q(last_name__icontains=last_name)
    if uno_code:
        query |= Q(unokod__icontains=uno_code)

    # Filter the clients only if query is not empty
    clients = Client.objects.filter(query) if query else Client.objects.none()

    return clients


@router.get("/guest/list", tags=["Volunteer"])
def list_guests(request):
    return {"status": "success"}, 200


@router.post("/guest/create", response=ClientSchema, tags=["Volunteer"])
def create_client(request, client_data: VolunteerCreateClientPostSchema):
    count = Client.objects.filter(unokod=client_data.uno).count()
    if count > 0:
        raise HttpError(409, "Client with the unocode exists already.")

    try:
        user = User()
        user.username = client_data.uno
        user.save()

        new_client = Client()
        new_client.user = User.objects.get(username=client_data.uno)
        new_client.first_name = client_data.first_name
        new_client.last_name = client_data.last_name
        new_client.unokod = client_data.uno
        new_client.gender = client_data.gender
        new_client.region = Region.objects.get(name=client_data.region)

        new_client.save()
    except Exception as e:
        raise HttpError(400, "Not able to create client.")

    return new_client


@router.post("/booking/request", response=BookingSchema, tags=["Volunteer"])
def request_booking(request, booking_data: VolunteerBookingPostSchema):
    try:
        product = Product.objects.get(id=booking_data.product_id)

        if not product.bookable:
            raise HttpError(422, "This product is not bookable.")

        Available.objects.filter(product=product)
    except Available.DoesNotExist:
        raise HttpError(404, "Product is not available")
    except Product.DoesNotExist:
        raise HttpError(404, "Product does not exist")

    user = Client.objects.get(id=booking_data.user_id)
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


@router.patch("/booking/confirm/{booking_id}", response=BookingSchema, tags=["Volunteer"])
def confirm_booking(request, booking_id: int):
    booking = Booking.objects.get(id=booking_id)
    if booking:
        if booking.status.description == "pending":
            raise HttpError(409, "Booking is pending and can't be confirmed.")
        else:
            return booking

    raise HttpError(404, "Booking does not exist.")