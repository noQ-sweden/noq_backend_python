from ninja import NinjaAPI, Schema, ModelSchema
from backend.models import (
    User,
    Host,
    Region,
    Product,
    Booking,
    ProductAvailable,
)
from typing import List
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date

api = NinjaAPI(csrf=False)


class RegionSchema(ModelSchema):
    """

    Region

    Exempelvis Stockholm City och Farsta

    Varje Host tillhör en Region
    """

    class Meta:
        model = Region
        fields = "__all__"


# Detta är mallen för en LIST-anrop
@api.get("/region", response=List[RegionSchema])
def region_list(request):
    list = Region.objects
    return list


class UserSchema(ModelSchema):
    """
    User - för både Brukare och användare i systemet

    Varje user tillhör en Region
    """

    # region: RegionSchema

    class Meta:
        model = User
        fields = "__all__"


# Mall för List
@api.get("/user", response=List[UserSchema])
def user_list(request):
    list = User.objects
    return list


# User Detail view
@api.get("/user/{user_id}", response=UserSchema)
def user_detail(request, user_id: int):
    obj = get_object_or_404(User, id=user_id)
    return obj


class UserPostSchema(Schema):
    """
    User för POST-anrop

    """

    first_name: str
    last_name: str
    gender: str
    phone: str
    email: str
    region_id: int
    unokod: str = None


# Mall för POST-anrop
@api.post("/user", response=UserSchema)
def create_user(request, payload: UserPostSchema):
    obj = User.objects.create(**payload.dict())
    return obj


class UserSchema(ModelSchema):
    """

    Host

    Exempelvis Stadsmissionen, Stockholm

    Varje Host tillhör en Region
    """

    region: RegionSchema

    class Meta:
        model = Host
        fields = "__all__"


# Mall för List
@api.get("/host", response=List[UserSchema])
def host_list(request):
    list = Host.objects
    return list


# Mall för Detail
@api.get("/host/{host_id}", response=UserSchema)
def host_detail(request, host_id: int):
    host = get_object_or_404(Host, id=host_id)
    return host


# Mall för Add dvs POST
class HostPostSchema(ModelSchema):
    """
    Host eller Härbärge för POST

    """

    region: int

    class Meta:
        model = Host
        exclude = ["id"]
        fields = "__all__"


## Mall för POST Add
@api.post("/host", response=UserSchema)
def create_host(request, payload: HostPostSchema):
    host = Host.objects.create(**payload.dict())
    return host


class HostPatchSchema(ModelSchema):
    class Meta:
        model = Host
        fields = ["id"]  # Note: all these fields are required on model level
        fields_optional = "__all__"


@api.patch("/host", response=UserSchema)
def host_edit(request, payload: HostPatchSchema):
    host = Host.objects.create(**payload.dict())
    return host


class ProductSchema(Schema):
    id: int
    name: str
    description: str
    total_places: int
    host: UserSchema = None
    type: str


@api.get("/product", response=List[ProductSchema])
def product_list(request):
    product_list = Product.objects.select_related("host")
    return product_list


@api.get("/product/{product_id}", response=ProductSchema)
def product_detail(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product


class BookingSchema(Schema):
    start_date: date
    product: ProductSchema
    user: UserSchema


@api.get("/booking", response=List[BookingSchema])
def list_booking(request):
    booking_list = Booking.objects.select_related("product")
    return booking_list


@api.get("/booking/{product_id}", response=BookingSchema)
def get_booking(request, product_id: int):
    booking = get_object_or_404(Booking, id=product_id)
    return booking


class Available(Schema):
    available_date: date
    product: ProductSchema
    places_left: int


@api.get("/available/{id}", response=Available)
def booking_detail(request, id: int):
    avail = get_object_or_404(Booking, id=id)
    return avail


# Only for testing api token functionality
class AuthBearer(HttpBearer):
    """
    AuthBearer för Authorization
    """

    def authenticate(self, request, token):
        if token == "supersecret":
            return token


# Only for testing api token functionality
@api.get("/bearer", auth=AuthBearer())
def bearer(request):
    return {"token": request.auth}
