from ninja import NinjaAPI, Schema, ModelSchema, Router
from backend.models import (
    UserDetails,
    Host,
    Region,
    Product,
    Booking,
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
    AuthBearer,
)

from typing import List
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date, timedelta

router = Router()

# User List view, demands django user logged on
@router.get("/users", response=List[UserSchema], tags=["Users"])
def users_list(request):
    qs = UserDetails.objects.all()
    return qs


# User Detail view
@router.get("/user/{user_id}", response=UserSchema, tags=["User Detail"])
def get_user(request, user_id: int):
    user = get_object_or_404(UserDetails, id=user_id)
    return user


# Mall för List
@router.get(
    "/user", auth=django_auth, response=List[UserSchema], tags=["User Authenticated"]
)
def user_list(request):
    list = UserDetails.objects
    return list


# Detta är mallen för en LIST-anrop
@router.get("/region", response=List[RegionSchema], tags=["Region"])
def region_list(request):
    list = Region.objects
    return list


# User Detail view
@router.get("/users/{user_id}", response=UserSchema, tags=["Users"])
def user_detail(request, user_id: int):
    obj = get_object_or_404(UserDetails, id=user_id)
    return obj


# Mall för POST-anrop
@router.post("/users", response=UserSchema, tags=["Users"])
def create_user(request, payload: UserPostSchema):
    obj = UserDetails.objects.create(**payload.dict())
    return obj


# Mall för List
@router.get("/hosts", response=List[HostSchema], tags=["Hosts"])
def host_list(request):
    list = Host.objects
    return list


# Mall för List
@router.get("/hosts/ids", tags=["List of host.id"])
def list_host_ids(request):
    host = Host.objects.first()

    values = Host.objects.all().values()
    values_list = Host.objects.all().values_list()
    ids = (22, 344)
    for o in values_list:
        ids.add(o.pk)

    return values


# Mall för Detail
@router.get("/hosts/{host_id}", response=HostSchema, tags=["Hosts"])
def host_detail(request, host_id: int):
    if host_id < 0:
        first = Host.objects.first()
        host_id = first.pk
    host = get_object_or_404(Host, id=host_id)
    return host


# Mall för sub lists
@router.get(
    "/hosts/{host_id}/products",
    response=list[ProductSchema],
    tags=["Host Products", "Products"],
)
def host_products(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)

    list = Product.objects.filter(host=host)
    return list


## Mall för POST Add
@router.post("/hosts", response=HostSchema, tags=["Hosts"])
def create_host(request, payload: HostPostSchema):
    host = Host.objects.create(**payload.dict())
    region_id = payload["region"]
    region = get_object_or_404(Region, id=region_id)
    host.region = region
    host.save()
    return host


# Mall för PATCH, dvs Update
@router.patch("/hosts/{host_id}", tags=["Hosts"])
def host_update(request, host_id: int, payload: HostPatchSchema):
    host = get_object_or_404(Host, id=host_id)
    for attr, value in payload.dict().items():
        if value:
            setattr(host, attr, value)
    host.save()

    return payload.dict(exclude_unset=True)


@router.get("/products", response=List[ProductSchema], tags=["Products"])
def product_list(request):
    product_list = Product.objects
    return product_list


@router.get("/products/{product_id}", response=ProductSchema, tags=["Products"])
def product_detail(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product


@router.get("/bookings/{delta_days}", response=List[BookingSchema], tags=["Bookings"])
def list_booking(request, delta_days: int):
    selected_date = date.today() + timedelta(days=delta_days)
    booking_list = Booking.objects.filter(start_date=selected_date)
    return booking_list


@router.get("/bookings/{product_id}", response=BookingSchema, tags=["Bookings"])
def booking_detail(request, product_id: int):
    booking = get_object_or_404(Booking, id=product_id)
    return booking


# Book a Product
@router.post("/bookings", response=BookingSchema, tags=["Bookings"])
def booking_add(request, data: BookingPostSchema):
    product = get_object_or_404(Product, id=data.product_id)
    user = get_object_or_404(UserDetails, id=data.user_id)
    booking = Booking.objects.create(
        start_date=data.start_date, product=product, user=user
    )
    return booking


@router.get("/available/{delta_days}", response=List[AvailableSchema], tags=["Available"])
def list_available(request, delta_days: int):
    selected_date = date.today() + timedelta(days=delta_days)
    list = Available.objects.filter(available_date=selected_date)
    return list


@router.get("/available/{id}", response=AvailableSchema, tags=["Available"])
def available_detail(request, id: int):
    avail = get_object_or_404(Booking, id=id)
    return avail


# Only for testing router token functionality
@router.get("/bearer", auth=AuthBearer(), tags=["x Authorization"])
def bearer(request):
    return {"token": request.auth}
