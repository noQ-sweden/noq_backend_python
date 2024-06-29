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

router = Router(auth=lambda request: group_auth(request, "host"))  # request defineras vid call, gruppnamnet är statiskt


@router.get("/count_bookings", response=BookingCounterSchema, tags=["host-frontpage"])
def count_bookings(request):
    host = Host.objects.get(users=request.user)

    pending_count = Booking.objects.filter(product__host=host, status__description='pending').count()
    arrivals_count = Booking.objects.filter(product__host=host, status__description='accepted',
                                            start_date=date.today()).count()
    departures_count = Booking.objects.filter(product__host=host, status__description='checked_in',
                                              start_date=date.today() - timedelta(days=1)).count()
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
def get_pending_bookings(request, limiter: Optional[
    int] = None):  # Limiter example /pending?limiter=10 for 10 results, empty returns all
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
        booking.status = BookingStatus.objects.get(description='accepted')
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")


@router.patch("/pending/{booking_id}/decline", response=BookingSchema, tags=["host-manage-requests"])
def decline_pending_booking(request, booking_id: int):
    host = Host.objects.get(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host=host, status__description='pending')

    try:
        booking.status = BookingStatus.objects.get(description='declined')
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")


@router.get("/bookings", response=BookingSchema, tags=["host-manage-bookings"])
def get_all_bookings(request, limiter: Optional[
    int] = None):  # Limiter example /pending?limiter=10 for 10 results, empty returns all
    host = Host.objects.get(users=request.user)
    bookings = Booking.objects.filter(product__host=host)

    if limiter is not None and limiter > 0:
        return bookings[:limiter]

    return bookings


# This API can be used to undo previous decision for accept or decline
# Bookings that have status checked_in can't be changed.
@router.patch("/bookings/{booking_id}/setpending", response=BookingSchema, tags=["host-manage-bookings"])
def set_booking_pending(request, booking_id: int):
    host = Host.objects.get(users=request.user)
    booking = get_object_or_404(Booking, id=booking_id, product__host=host)

    try:
        booking.status = BookingStatus.objects.get(description='pending')
        booking.save()
        return booking
    except BookingStatus.DoesNotExist:
        raise HttpError(404, detail="Booking status does not exist.")


# Mall för List
@router.get("/hosts", response=List[HostSchema], tags=["Hosts"])
def host_list(request):
    list = Host.objects
    return list


# List products for specific host
@router.get(
    "/hosts/{host_id}/products",
    response=list[ProductSchema],
    tags=["Host Products", "Products"],
)
def host_products(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)
    list = Product.objects.filter(host=host)
    return list


# List all products
@router.get("/products", response=List[ProductSchema], tags=["Products"])
def product_list(request):
    product_list = Product.objects
    return product_list


# Get details of a single product by ID
@router.get("/products/{product_id}", response=ProductSchema, tags=["Products"])
def product_detail(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product


# Create a new product
@router.post("/products/create", response=ProductSchema, tags=["Products"])
def product_create(request, payload: ProductSchema):
    host = get_object_or_404(Host, id=payload.host.id)
    product = Product(
        name=payload.name,
        description=payload.description,
        total_places=payload.total_places,
        host=host,
        type=payload.type
    )
    product.save()
    return product


@router.put("/products/{product_id}/update", response=ProductSchema, tags=["Products"])
def product_update(request, product_id: int, payload: ProductSchema):
    product = get_object_or_404(Product, id=product_id)

    for attr, value in payload.dict().items():
        if attr == "host":
            host = get_object_or_404(Host, id=value["id"])
            setattr(product, attr, host)
        else:
            setattr(product, attr, value)
    product.save()

    return product


@router.delete("/products/{product_id}", response=dict, tags=["Products"])
def product_delete(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"message": "Product deleted successfully"}