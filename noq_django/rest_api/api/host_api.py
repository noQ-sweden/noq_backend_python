from django.db.models import Q
from ninja import NinjaAPI, Schema, ModelSchema, Router
from ninja.errors import HttpError
from datetime import datetime, timedelta
from django.db import transaction

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
)

from backend.auth import group_auth

from typing import List, Dict, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

router = Router(auth=lambda request: group_auth(request, "host"))  # request defineras vid call, gruppnamnet är statiskt

# api/host/ returns the host information
@router.get("/", response=HostSchema, tags=["host-frontpage"])
def get_host_data(request):
    try:
        host = Host.objects.get(users=request.user)
        return host
    except Host.DoesNotExist:
        raise HttpError(200, "User is not admin to a host.")

@router.get("/count_bookings", response=BookingCounterSchema, tags=["host-frontpage"])
def count_bookings(request):
    host = Host.objects.get(users=request.user)

    pending_count = Booking.objects.filter(product__host=host, status__description='pending').count()
    arrivals_count = Booking.objects.filter(
        product__host=host,
        status__description__in=['accepted', 'reserved', 'confirmed'],
        start_date=date.today()
    ).count()
    departures_count = Booking.objects.filter(product__host=host, status__description='checked_in',
                                              end_date=date.today()).count()
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

@router.get("/available/{nr_of_days}", response=AvailablePerDateSchema, tags=["host-frontpage"])
def get_available_places(request, nr_of_days: int):
    host = Host.objects.get(users=request.user)
    current_date = datetime.today().date()
    # Dictionary with product name : available places
    available_places = {}
    products = Product.objects.filter(host_id=host)
    for day in range(nr_of_days):
        available_for_day = []
        available_date = current_date + timedelta(days=day)
        # Exclude bookings with status declined and in_queue
        for product in products:
            available = Available.objects.filter(
                product=product,
                available_date=available_date
            ).first()

            if available:
                places_left = available.places_left
            else:
                places_left = product.total_places

            available_for_day.append(
                AvailableSchema(
                    id=product.id,
                    available_date=available_date,
                    product=product,
                    places_left=places_left
                )
            )
        available_places[str(available_date)] = available_for_day
    return AvailablePerDateSchema(available_dates=available_places)


@router.get("/bookings/incoming", response=List[BookingSchema], tags=["host-frontpage"])
def get_bookings_by_date(request, limiter: Optional[
    int] = None):  # Limiter example /bookings/incoming?limiter=10 for 10 results, empty returns all
    host = Host.objects.get(users=request.user)
    current_date = datetime.today().date()
    bookings = Booking.objects.filter(
        product__host=host,
        start_date=current_date)

    if limiter is not None and limiter > 0:
        return bookings[:limiter]

    return bookings


@router.get("/bookings/outgoing", response=List[BookingSchema], tags=["host-frontpage"])
def get_bookings_by_date(request, limiter: Optional[
    int] = None):  # Limiter example /bookings/outgoing?limiter=10 for 10 results, empty returns all
    host = Host.objects.get(users=request.user)
    current_date = datetime.today().date()
    bookings = Booking.objects.filter(
        product__host=host,
        end_date=current_date)

    if limiter is not None and limiter > 0:
        return bookings[:limiter]

    return bookings


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

@router.patch("/pending/bulk/accept", response={200: dict, 400: dict}, tags=["caseworker-manage-requests"])
def bulk_appoint_pending_booking(request, booking_ids: list[BookingUpdateSchema]):
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

    return 200, {'message': 'Bulk update successful'}


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
    hosts_list = Host.objects
    return hosts_list


# List products for specific host
@router.get(
    "/hosts/{host_id}/products",
    response=list[ProductSchema],
    tags=["Host Products", "Products"],
)
def host_products(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)
    products_list = Product.objects.filter(host=host)
    return products_list


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
@router.post("/products", response={201: ProductSchema}, tags=["Products"])
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


@router.put("/products/{product_id}/edit", response=ProductSchema, tags=["Products"])
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

# Get a list of all invoices
@router.get("/invoices", response=List[InvoiceResponseSchema], tags=["Invoice"])
def list_invoices(request):
    invoices = Invoice.objects.all()
    return invoices


# Get a specific invoice
@router.get("/invoices/{invoice_id}", response=InvoiceResponseSchema, tags=["Invoice"])
def get_invoice(request, invoice_id: int):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return invoice


# Create a new invoice
@router.post("/invoices", response=InvoiceResponseSchema, tags=["Invoice"])
def create_invoice(request, payload: InvoiceCreateSchema):
    host = get_object_or_404(Host, id=payload.host)
    status = get_object_or_404(InvoiceStatus, name=payload.status)
    invoice = Invoice.objects.create(
        host=host,
        amount=payload.amount,
        description=payload.description,
        due_date=payload.due_date,
        currency=payload.currency,
        invoice_number=payload.invoice_number,
        vat_rate=payload.vat_rate,
        sale_date=payload.sale_date,
        seller_vat_number=payload.seller_vat_number,
        buyer_vat_number=payload.buyer_vat_number,
        buyer_name=payload.buyer_name,
        buyer_address=payload.buyer_address,
        status=status
    )
    return invoice