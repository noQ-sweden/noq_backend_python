from datetime import date
from http.client import HTTPException
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from email.utils import parsedate
from ninja import Router
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from pydantic import BaseModel, ValidationError
from backend.models import UserProfile
from backend.models import User
from ninja.errors import HttpError

from .services import update_user_profile
from .api_schemas import UserProfileCreateSchema, UserProfileOut, UserProfileUpdateSchema
from ninja.security import HttpBasicAuth
from django.contrib.auth import authenticate

preference_router = Router(tags=["Preferences"])

from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    BookingStatus,
    Available,
    VolunteerProfile,
    VolunteerHostAssignment,
    User,
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
    AvailableProductsSchema,
    ProductSchemaWithPlacesLeft,
    UserIDSchema,
    ClientSchema,
    VolunteerCreateClientPostSchema,
    SimplifiedClientSchema,
    UserProfileCreateSchema,
    UserProfileUpdateSchema,
    UserProfileOut,
)


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            return user

basic_auth = BasicAuth()
# preference_router = Router(auth=basic_auth)
preference_router = Router(auth=None)
# @preference_router.get("/test")
# def test_view(request):
#     return {"message": "Test successful"}


@preference_router.get("/", response=list[UserProfileOut])
def list_profiles(request):
    profiles = UserProfile.objects.all()
    return profiles


# READ user profile (by ID)
@preference_router.get("/{user_id}", response=UserProfileOut)
def get_profile(request, user_id: int):
    if request.user.id != user_id:
        raise HttpError(403, "Not authorized to access this profile")

    profile = UserProfile.objects.filter(user__id=user_id).first()
    if not profile:
        raise HttpError(404, "User profile not found")
    return profile

class SuccessResponseSchema(BaseModel):
    success: bool
    profile_id: int
    
# UPDATE user profile
@preference_router.patch("/{user_id}", response=UserProfileCreateSchema)
def update_profile(request, user_id: int, data: UserProfileUpdateSchema):
    try:
        profile = update_user_profile(user_id=user_id, data=data.dict(exclude_unset=True))
        return profile
    except ValidationError as e:
         raise HttpError(400,str(e))
    
# DELETE user profile
@preference_router.delete("/{user_id}")
def delete_profile(request, user_id: int):
    if request.user.id != user_id:
        raise HttpError(403, "Not authorized to delete this profile")

    profile = UserProfile.objects.filter(user__id=user_id).first()
    if not profile:
        raise HttpError(404, "User profile not found")
    profile.delete()
    return {"success": True}

@preference_router.post("/", response=UserProfileOut)
def create_profile(request, payload: UserProfileCreateSchema):
    user = request.user

    if UserProfile.objects.filter(user=user).exists():
        raise HttpError(400, "Profile already exists")

    if UserProfile.objects.filter(uno=payload.uno).exists():
        raise HttpError(400, "UNO already exists")

    supporting_person = None
    if payload.supporting_person_id:
        supporting_person = get_object_or_404(User, id=payload.supporting_person_id)

    profile = UserProfile.objects.create(
        user=user,
        uno=payload.uno,
        first_name=payload.first_name,
        last_name=payload.last_name,
        sex=payload.sex,
        birthday=payload.birthday,
        birth_year=payload.birth_year,
        email=payload.email,
        telephone=payload.telephone or "",
        language=payload.language,
        presentation=payload.presentation or "",
        supporting_person=supporting_person
    )

    return profile

# @preference_router.post("/profile", response={200: dict, 400: str})
# def create_profile(request, payload: UserProfileCreateSchema):
#     if hasattr(request.user, 'profile'):
#         return 400, "Profile already exists"
    
#     profile = UserProfile.objects.create(
#         user=request.user,
#         uno=payload.uno,
#         first_name=payload.first_name,
#         last_name=payload.last_name,
#         sex=payload.sex,
#         birthday=payload.birthday,
#         birth_year=payload.birth_year,
#         email=payload.email,
#         telephone=payload.telephone,
#         language=payload.language or 'sv',
#         presentation=payload.presentation,
#         supporting_person_id=payload.supporting_person_id
#     )
#     return {"id": profile.id, "message": "Profile created"}

# @preference_router.get("/profile", response={200: dict, 404: str})
# def get_profile(request):
#     if not hasattr(request.user, 'profile'):
#         return 404, "Profile not found"
    
#     p = request.user.profile
#     return {
#         "uno": p.uno,
#         "first_name": p.first_name,
#         "last_name": p.last_name,
#         "email": p.email,
#         "telephone": p.telephone,
#         "language": p.language,
#         "presentation": p.presentation,
#         "supporting_person": p.supporting_person.username if p.supporting_person else None
#     }

# @preference_router.patch("/profile", response={200: dict, 400: str})
# def update_profile(request, payload: UserProfileUpdateSchema):
#     if not hasattr(request.user, 'profile'):
#         return 400, "Profile does not exist"
    
#     profile = request.user.profile

#     for field, value in payload.dict(exclude_unset=True).items():
#         setattr(profile, field, value)

#     profile.save()
#     return {"message": "Profile updated"}

# @preference_router.delete("/profile", response={200: dict})
# def delete_me(request):
#     # Soft delete — deactivate account
#     request.user.is_active = False
#     request.user.save()
#     return {"message": "Your account has been deactivated"}
