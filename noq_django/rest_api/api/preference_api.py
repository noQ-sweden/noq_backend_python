from typing import List
from ninja import File, Router
from ninja.files import UploadedFile
from .api_schemas import UserProfileCreateSchema, UserProfileOut, UserProfileUpdateSchema
from backend.models import UserProfile, Client
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

preference_router = Router(tags=["Preferences"])

@preference_router.get("/{user_id}", response=UserProfileOut)
def get_profile(request, user_id: int):
    if request.user.id != user_id:
        raise HttpError(403, "You are not authorized to view this profile")
    profile = get_object_or_404(UserProfile, user__id=user_id)
    return UserProfileOut(
        id=profile.id,
        user_id=profile.user.id,
        uno=profile.client.unokod,
        first_name=profile.user.first_name,
        last_name=profile.user.last_name,
        sex=profile.client.gender if hasattr(profile, "client") and profile.client else None,
        email=profile.user.email,
        language=profile.language,
        avatar=profile.avatar.url if profile.avatar else None,
        presentation=profile.presentation,
        supporting_person_id=profile.supporting_person.id if profile.supporting_person else None,
    )

@preference_router.get("/", response=List[UserProfileOut])
def list_profiles(request):
    profiles = UserProfile.objects.all()
    return [
        UserProfileOut(
            id=profile.id,
            user_id=profile.user.id,
            uno=profile.client.unokod,
            first_name=profile.user.first_name,
            last_name=profile.user.last_name,
            sex=profile.client.gender if hasattr(profile, "client") and profile.client else None,
            email=profile.user.email,
            language=profile.language,
            avatar=profile.avatar.url if profile.avatar else None,
            presentation=profile.presentation,
            supporting_person_id=profile.supporting_person.id if profile.supporting_person else None,
        )
        for profile in profiles
    ]

@preference_router.post("/", response=UserProfileOut)
def create_profile(
    request,
    payload: UserProfileCreateSchema,
):
    user = request.user

    if UserProfile.objects.filter(user=user).exists():
        raise HttpError(400, "Profile already exists")

    try:
        client = get_object_or_404(Client, user=user)
        # Add this check:
        if Client.objects.filter(unokod=client.unokod).exclude(user=user).exists():
            raise HttpError(400, "Client with this uno already exists")
        supporting_person = None
        if payload.supporting_person_id:
            supporting_person = get_object_or_404(User, id=payload.supporting_person_id)

        profile = UserProfile.objects.create(
            user=user,
            client=client,
            language=payload.language or 'sv',
            presentation=payload.presentation or "",
            supporting_person=supporting_person
        )

        return UserProfileOut(
            id=profile.id,
            user_id=profile.user.id,
            uno=profile.client.unokod,
            first_name=profile.user.first_name,
            last_name=profile.user.last_name,
            sex=profile.client.gender if hasattr(profile, "client") and profile.client else None,
            email=profile.user.email,
            language=profile.language,
            avatar=profile.avatar.url if profile.avatar else None,
            presentation=profile.presentation,
            supporting_person_id=profile.supporting_person.id if profile.supporting_person else None,
        )
    except Exception as e:
        raise HttpError(400, str(e))
    
@preference_router.patch("/{user_id}", response=UserProfileOut)
def update_profile(
    request,
    user_id: int,
    payload: UserProfileUpdateSchema,
     
):
    if request.user.id != user_id:
        raise HttpError(403, "Not authorized to update this profile")

    profile = get_object_or_404(UserProfile, user__id=user_id)
    data = payload.dict(exclude_unset=True)

    if "language" in data:
        profile.language = data["language"]
    if "presentation" in data:
        profile.presentation = data["presentation"]
    if "supporting_person_id" in data:
        if data["supporting_person_id"] is not None:
            profile.supporting_person = get_object_or_404(User, id=data["supporting_person_id"])
        else:
            profile.supporting_person = None

     
    profile.save()

    return UserProfileOut(
        id=profile.id,
        user_id=profile.user.id,
        uno=profile.client.unokod,
        first_name=profile.user.first_name,
        last_name=profile.user.last_name,
        sex=profile.client.gender if hasattr(profile, "client") and profile.client else None,
        email=profile.user.email,
        language=profile.language,
        avatar=profile.avatar.url if profile.avatar else None,
        presentation=profile.presentation,
        supporting_person_id=profile.supporting_person.id if profile.supporting_person else None,
    )

@preference_router.delete("/{user_id}", response={200: dict})
def delete_profile(request, user_id: int):
    if request.user.id != user_id:
        raise HttpError(403, "You are not authorized to delete this profile")
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.delete()
    return {"success": True}