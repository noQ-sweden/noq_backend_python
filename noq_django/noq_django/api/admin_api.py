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

@router.get("/hosts", response=List[HostSchema], tags=["Hosts"])
def host_list(request):
    list = Host.objects
    return list