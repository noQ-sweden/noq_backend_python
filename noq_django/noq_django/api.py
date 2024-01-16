from ninja import NinjaAPI, Schema
from backend.models import User, Host
from typing import List
from django.shortcuts import get_object_or_404

api = NinjaAPI()


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


# User List view
@api.get("/user", response=List[UserOut])
def list_users(request):
    qs = User.objects.all()
    return qs


# User Detail view
@api.get("/user/{user_id}", response=UserOut)
def get_employee(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user


@api.post("/user", response=UserOut)
def create_user(request, payload: UserIn):
    user = User.objects.create(**payload.dict())
    return user


class HostIn(Schema):
    name: str
    street: str
    city: str
    total_available_places: int


# Response to creating host
class HostOut(Schema):
    id: int
    name: str
    street: str
    city: str
    total_available_places: int


@api.post("/host", response=HostOut)
def create_host(request, payload: HostIn):
    host = Host.objects.create(**payload.dict())
    return host
