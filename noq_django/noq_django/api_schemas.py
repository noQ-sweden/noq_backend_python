from ninja import NinjaAPI, Schema, ModelSchema

from backend.models import (
    User,
    Host,
    Region,
    Product,
    Booking,
    Available,
)

from typing import List
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date, timedelta


class RegionSchema(ModelSchema):
    """

    Region

    Exempelvis Stockholm City och Farsta

    Varje Host tillhör en Region
    """

    class Meta:
        model = Region
        fields = "__all__"


class UserSchema(ModelSchema):
    """
    User - för både Brukare och användare i systemet

    Varje user tillhör en Region
    """

    region: RegionSchema

    class Meta:
        model = User
        fields = "__all__"


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


class HostSchema(ModelSchema):
    """

    Host

    Exempelvis Stadsmissionen, Stockholm

    Varje Host tillhör en Region
    """

    region: RegionSchema

    class Meta:
        model = Host
        fields = "__all__"


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


class HostPatchSchema(ModelSchema):
    """
    Host eller Härbärge för PATCH (update)

    """
    
    class Meta:
        model = Host
        fields = ["id"]  # Note: all these fields are required on model level
        fields_optional = "__all__"


class ProductSchema(Schema):
    """
    Product
    Product är en generalisering istället för exempelvis Room 
    som gör det möjligt att Härbärge kan erbjuda många tjänster. 
    Exempelvis rum eller luncher
    """
    id: int
    name: str
    description: str
    total_places: int
    host: HostSchema = None
    type: str


class BookingSchema(Schema):
    """
    Booking för att boka en Product
    
    """
    start_date: date
    product: ProductSchema
    user: UserSchema


class AvailableSchema(Schema):
    """
    Available för att kunna se om en Product har tillgängliga platser
    
    """
    id: int
    available_date: date
    product: ProductSchema
    places_left: int


# Only for testing api token functionality
class AuthBearer(HttpBearer):
    """
    AuthBearer för Authorization
    """

    def authenticate(self, request, token):
        if token == "supersecret":
            return token
