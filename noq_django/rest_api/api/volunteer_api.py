from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from typing import Optional
from django.db import models
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from backend.auth import group_auth
from typing import List
import json
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date
from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    BookingStatus,
    Available,
    VolunteerProfile,
    VolunteerHostAssignment,
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
    BookingPostSchema,
    AvailableSchema,
    AvailableProductsSchema,
    ProductSchemaWithPlacesLeft,
    UserIDSchema,
    ClientSchema,
    VolunteerCreateClientPostSchema,
)

router = Router(auth=lambda request: group_auth(request, "volunteer"))

# TODO: Test live email server setup to ensure delivery in production
# TODO: Use the created modules for volunteer profile when confirming bookings to make sure they have the right to request booking at the specific host

def send_confirmation_to_guest(email, booking):
    message = f"""
    Hej {booking.user.first_name} {booking.user.last_name},

    Din bokning för {booking.product.name} har bekräftats.
    Startdatum: {booking.start_date}
    Slutdatum: {booking.end_date}

    Tack så mycket!
    """
    send_mail(
        subject="Booking Confirmation",
        message=message,
        from_email="noreply@yourdomain.com", #not sure what our domain is :) will need to be updated
        recipient_list=[email],
        fail_silently=False,
    )


@router.get("/available", response=List[AvailableProductsSchema], tags=["Volunteer"])
def list_available(request, selected_date: Optional[str] = None, host_id: Optional[int] = None):
    # Validate and parse date if provided
    if selected_date:
        try:
            selected_date = models.DateField().to_python(selected_date)
        except ValueError:
            raise HttpError(404, "Invalid date, dates need to be in the YYYY-MM-DD format")

    # Initialize the query for products
    products = Product.objects.all()

    # Filter by host if host_id is provided
    if host_id:
        try:
            host = Host.objects.get(id=host_id)
            products = products.filter(host=host)
        except Host.DoesNotExist:
            raise HttpError(404, "Host not found")

    # Filter by availability date if selected_date is provided
    if selected_date:
        unavailable_products = Available.objects.filter(available_date=selected_date, places_left=0)
        products = products.exclude(id__in=unavailable_products.values('product_id'))

    # Build dictionary of products organized by host
    hostproduct_dict = {}
    for product in products:
        if selected_date:
            available = Available.objects.filter(available_date=selected_date, product=product)
            places_left = available.first().places_left if available.exists() else product.total_places
        else:
            available = Available.objects.filter(product=product, places_left__gt=0).order_by('available_date')
            places_left = available.first().places_left if available.exists() else product.total_places
        product.places_left = places_left

        if product.host in hostproduct_dict:
            hostproduct_dict[product.host].append(product)
        else:
            hostproduct_dict[product.host] = [product]

    return [{"host": HostSchema.from_orm(host), "products": products} for host, products in hostproduct_dict.items()]


@router.post("/booking/request", response=BookingSchema, tags=["Volunteer"])
def request_booking(request, booking_data: BookingPostSchema):
    # Validate that end_date is after start_date
    if booking_data.end_date <= booking_data.start_date:
        raise HttpError(422, "End date must be after start date.")

    # Check if an identical booking already exists
    existing_booking = Booking.objects.filter(
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        product_id=booking_data.product_id,
        user_id=booking_data.user_id
    ).first()

    if existing_booking:
        raise HttpError(409, "A booking with these details already exists.")

    # Proceed with creating a new booking if no duplicate is found
    try:
        product = Product.objects.get(id=booking_data.product_id)

        if not product.bookable:
            raise HttpError(422, "This product is not bookable.")

        # Check availability
        Available.objects.filter(product=product)
    except Available.DoesNotExist:
        raise HttpError(404, "Product is not available")
    except Product.DoesNotExist:
        raise HttpError(404, "Product does not exist")

    # Use provided user_id if volunteer is making booking for another user
    user = get_object_or_404(Client, id=booking_data.user_id)

    booking = Booking(
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        product=product,
        user=user,
        status=BookingStatus.objects.get(description="pending")
    )

    try:
        booking.save()
    except Exception as e:
        if hasattr(e, 'code') and e.code == "full":
            raise HttpError(200, json.dumps(e.params))

    return booking


@router.patch("/booking/confirm/{booking_id}", response=BookingSchema, tags=["Volunteer"])
def confirm_booking(request, booking_id: int):
    # Retrieve the booking and validate its existence
    booking = get_object_or_404(Booking, id=booking_id)

    # Ensure booking status allows for confirmation (if you want a condition)
    if booking.status.description != "pending":
        raise HttpError(400, "Only pending bookings can be confirmed.")

    # Retrieve the user associated with the booking
    user = booking.user
    print(user.__dict__)

    # Update booking status to reflect confirmation
    booking.status = BookingStatus.objects.get(description="confirmed")

    try:
        booking.save()
    except Exception as e:
        raise HttpError(400, json.dumps(e.params))

    # Check if the guest has contact information
    if user.email:
        # Send confirmation
        send_confirmation_to_guest(user.email, booking)

    return booking


@router.get("/guest/search", response=List[ClientSchema], tags=["Volunteer"])
def search_guest(
    request,
    first_name: Optional[str] = "",
    last_name: Optional[str] = "",
    unocode: Optional[str] = ""):

    # Check if both fields are empty
    if not first_name.strip() and not last_name.strip() and not unocode.strip():
        raise HttpError(400, "Either first name, last name or unocode must be provided for the search.")

    # Search for users by first and last name and unocode, case-insensitive
    query = Q()
    if first_name:
        query |= Q(first_name__icontains=first_name)
    if last_name:
        query |= Q(last_name__icontains=last_name)
    if unocode:
        query |= Q(unokod__icontains=unocode)

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

#based on if we want to filter volunteer + associated with host and show only those records.
"""
@router.get("/available/{selected_date}", response=List[AvailableProductsSchema], tags=["volunteer-booking"])
def list_available(request, selected_date: str):
    try:
        selected_date = models.DateField().to_python(selected_date)
    except ValueError:
        raise HttpError(404, "Invalid date, dates need to be in the YYYY-MM-DD format")

    # Get the volunteer profile of the logged-in user
    try:
        volunteer_profile = VolunteerProfile.objects.get(user=request.user)
    except VolunteerProfile.DoesNotExist:
        raise HttpError(404, "Volunteer profile not found")

    # Find the active host for the volunteer
    active_host_assignment = volunteer_profile.host_assignments.filter(active=True).first()
    if not active_host_assignment:
        raise HttpError(404, "No active host assigned to this volunteer")

    # Get the active host
    active_host = active_host_assignment.host

    # List of unavailable products for the selected date and host
    unavailable_products = Available.objects.filter(
        available_date=selected_date, places_left=0, product__host=active_host
    )

    # Get available products for the active host
    available_products_list = Product.objects.filter(host=active_host).exclude(id__in=unavailable_products.values('product_id'))

    # Organize available products by host
    hostproduct_dict = {}
    for product in available_products_list:
        available = Available.objects.filter(available_date=selected_date, product=product)
        places_left = available.first().places_left if available.exists() else product.total_places
        product.places_left = places_left
        if product.host in hostproduct_dict:
            hostproduct_dict[product.host].append(product)
        else:
            hostproduct_dict[product.host] = [product]

    return [{"host": host, "products": products} for host, products in hostproduct_dict.items()]

"""