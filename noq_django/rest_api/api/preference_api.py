from typing import List
from ninja import File, Router
from ninja.files import UploadedFile
from .api_schemas import UserProfileCreateSchema, UserProfileOut, UserProfileUpdateSchema
from backend.models import UserProfile,Client
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
        user_id=profile.user.id,
        uno=profile.uno,
        first_name=profile.user.first_name,
        last_name=profile.user.last_name,
        sex=profile.sex,
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
            uno=profile.uno,
            first_name=profile.user.first_name,
            last_name=profile.user.last_name,
            sex=profile.sex,
            email=profile.user.email,
            language=profile.language,
            avatar=profile.avatar.url if profile.avatar else None,
            presentation=profile.presentation,
            supporting_person_id=profile.supporting_person.id if profile.supporting_person else None,
        )
        for profile in profiles
    ]

# @preference_router.get("/", response=List[UserProfileOut])
# def list_profiles(request):
#     profiles = UserProfile.objects.filter(user=request.user)
#     return UserProfileOut(
#         user_id=profiles.user.id,
#         uno=profiles.uno,
#         first_name=profiles.user.first_name,
#         last_name=profiles.user.last_name,
#         sex=profiles.sex,
#         email=profiles.user.email,
#         language=profiles.language,
#         avatar=profiles.avatar.url if profiles.avatar else None,
#         presentation=profiles.presentation,
#         supporting_person_id=profiles.supporting_person.id if profiles.supporting_person else None,
#     )

@preference_router.post("/", response=UserProfileOut)
def create_profile(
    request,
    payload: UserProfileCreateSchema,
    avatar: UploadedFile = File(None),
):
    user = request.user

    if hasattr(user, 'profile'):
        raise HttpError(400, "Profile already exists")

    try:
        client = get_object_or_404(Client, user=user)

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

        if avatar:
            profile.avatar.save(avatar.name, avatar.file, save=True)

        return profile

    except Exception as e:
        raise HttpError(400, str(e))
    

@preference_router.patch("/{user_id}", response=UserProfileOut)
def update_profile(
    request,
    user_id: int,
    payload: UserProfileUpdateSchema,
    avatar: UploadedFile = File(None),
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

    if avatar:
        profile.avatar.save(avatar.name, avatar.file, save=True)

    profile.save()
    return profile
