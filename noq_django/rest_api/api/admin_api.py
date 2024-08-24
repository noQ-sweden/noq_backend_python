from ninja import NinjaAPI, Schema, ModelSchema, Router
from backend.models import (
    Client,
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
)

from backend.auth import group_auth

from typing import List
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date, timedelta


router = Router(auth=lambda request: group_auth(request, "so_admin")) #request defineras vid call, gruppnamnet är statiskt