from ninja import NinjaAPI, Schema, ModelSchema
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

api = NinjaAPI(csrf=False)

documentation = """

    Generell namnsättning för alla API:er
    
    /objects    GET     listar ett objekt, med metodnamn objects_list, kan även ha filterparametrar
    /objects/id GET     hämtar en unik instans av objekt(/objects/id), med metodnamn object_detail(id)
    /objects/id POST    skapar ett objekt, med metodnamn object_add
    /objects/id PATCH   uppdaterar ett objekt, med metodnamn object_update(id)
    /objects/id DELETE  tar bort ett objekt, med metodnamn object_delete(id)

"""


# User List view, demands django user logged on
@api.get("/users", response=List[UserSchema])
def users_list(request):
    qs = UserDetails.objects.all()
    return qs


# User Detail view
@api.get("/user/{user_id}", response=UserSchema)
def get_user(request, user_id: int):
    user = get_object_or_404(UserDetails, id=user_id)
    return user


# Detta är mallen för en LIST-anrop
@api.get("/region", response=List[RegionSchema])
def region_list(request):
    list = Region.objects
    return list


# Mall för List
@api.get("/users", auth=django_auth, response=List[UserSchema])
def user_list(request):
    list = UserDetails.objects
    return list


# User Detail view
@api.get("/users/{user_id}", response=UserSchema)
def user_detail(request, user_id: int):
    obj = get_object_or_404(UserDetails, id=user_id)
    return obj


# Mall för POST-anrop
@api.post("/users", response=UserSchema)
def create_user(request, payload: UserPostSchema):
    obj = UserDetails.objects.create(**payload.dict())
    return obj


# Mall för List
@api.get("/hosts", response=List[HostSchema])
def host_list(request):
    list = Host.objects
    return list


# Mall för Detail
@api.get("/hosts/{host_id}", response=HostSchema)
def host_detail(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)
    return host


# Mall för sub lists
@api.get("/hosts/{host_id}/products", response=list[ProductSchema])
def host_detail(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)

    list = Product.objects.filter(host=host)
    return list


## Mall för POST Add
@api.post("/hosts", response=UserSchema)
def create_host(request, payload: HostPostSchema):
    host = Host.objects.create(**payload.dict())
    return host


## Mall för PATCH, dvs Update
@api.patch("/hosts", response=UserSchema)
def host_update(request, payload: HostPatchSchema):
    pass
    # not implemented yet
    # host = Host.objects.create(**payload.dict())
    # return host


@api.get("/products", response=List[ProductSchema])
def product_list(request):
    product_list = Product.objects
    return product_list


@api.get("/products/{product_id}", response=ProductSchema)
def product_detail(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product


@api.get("/bookings/{delta_days}", response=List[BookingSchema])
def list_booking(request, delta_days: int):
    selected_date = date.today() + timedelta(days=delta_days)
    booking_list = Booking.objects.filter(start_date=selected_date)
    return booking_list


@api.get("/bookings/{product_id}", response=BookingSchema)
def booking_detail(request, product_id: int):
    booking = get_object_or_404(Booking, id=product_id)
    return booking


# Book a Product
@api.post("/bookings", response=BookingSchema)
def booking_add(request, data: BookingPostSchema):
    product = get_object_or_404(Product, id=data.product_id)
    user = get_object_or_404(UserDetails, id=data.user_id)
    booking = Booking.objects.create(
        start_date=data.start_date, product=product, user=user
    )
    return booking


@api.get("/available/{delta_days}", response=List[AvailableSchema])
def list_available(request, delta_days: int):
    selected_date = date.today() + timedelta(days=delta_days)
    list = Available.objects.filter(available_date=selected_date)
    return list


@api.get("/available/{id}", response=AvailableSchema)
def available_detail(request, id: int):
    avail = get_object_or_404(Booking, id=id)
    return avail


# Only for testing api token functionality
@api.get("/bearer", auth=AuthBearer())
def bearer(request):
    return {"token": request.auth}
