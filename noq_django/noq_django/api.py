from ninja import NinjaAPI, Schema
from backend.models import User, Host, Product, ProductBooking, ProductAvailable
from typing import List
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, HttpBearer
from datetime import date

api = NinjaAPI(csrf=True)


class UserIn(Schema):
    first_name: str
    last_name: str
    gender: str
    phone: str
    email: str
    unokod: str = None


# Response model 1 - we can have several
class UserOut(Schema):
    id: int
    first_name: str
    last_name: str
    gender: str


# User List view, demands django user logged on
@api.get("/user", auth=django_auth, response=List[UserOut])
def list_users(request):
    qs = User.objects.all()
    return qs


# User Detail view
@api.get("/user/{user_id}", response=UserOut)
def get_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user


@api.post("/user", response=UserOut)
def create_user(request, payload: UserIn):
    user = User.objects.create(**payload.dict())
    return user


class HostIn(Schema):
    host_name: str
    street: str
    postcode: str
    city: str
    total_available_places: int


# Response to creating host
class HostOut(Schema):
    id: int
    host_name: str
    street: str
    postcode: str
    city: str
    total_available_places: int


@api.post("/host", response=HostOut)
def create_host(request, payload: HostIn):
    host = Host.objects.create(**payload.dict())
    return host


@api.get("/host", response=List[HostOut])
def list_host(request):
    qs = Host.objects.all()
    return qs


@api.get("/host/{host_id}", response=HostOut)
def get_host(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)
    return host


class ProductDetail(Schema):
    id: int
    name: str
    description: str
    total_places: int
    host: HostOut = None
    type: str


@api.get("/product", response=List[ProductDetail])
def list_product(request):
    product_list = Product.objects.select_related("host")
    return product_list


@api.get("/product/{product_id}", response=ProductDetail)
def get_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product


# class BookingDetail(Schema):
#     start_date: date
#     # product: Product
#     # user: User


# @api.get("/booking/{product_id}", response=BookingDetail)
# def get_booking(request, product_id: int):
#     booking = get_object_or_404(ProductBooking, id=product_id)
#     return booking


# class BookingAvailable(Schema):
#     available_date: date
#     # product: Product
#     # places_left: int


# @api.get("/available/{product_id}", response=BookingAvailable)
# def get_booking_availability(request, product_id: int):
#     avail = get_object_or_404(ProductBooking, id=product_id)
#     return avail


# Only for testing api token functionality
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


# Only for testing api token functionality
@api.get("/bearer", auth=AuthBearer())
def bearer(request):
    return {"token": request.auth}
