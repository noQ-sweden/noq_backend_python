from types import NoneType

from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from datetime import date, datetime

from backend.models import Client, UserProfile
from backend.auth import group_auth
from .api_schemas import (
    VolunteerUserProfileSchema,
    VolunteerProfileUpdateSchema,
    PasswordChangeSchema,
)

router = Router(auth=lambda request: group_auth(request, "volunteer"))


@router.get("/my_profile", response={200: VolunteerUserProfileSchema, 404: dict}, tags=["Profile"])
def get_my_profile(request):
    """
    Get current logged-in user's profile information.
    Creates UserProfile if it doesn't exist.
    """
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return 404, {"error": "Användarprofilen hittades inte."}
    
    # Get or create UserProfile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'client': client}
    )

    # Build avatar URL if avatar exists
    avatar_url = None
    if user_profile.avatar:
        avatar_url = request.build_absolute_uri(user_profile.avatar.url)
    
    return VolunteerUserProfileSchema(
        first_name=request.user.first_name,
        last_name=request.user.last_name,
        email=request.user.email,
        phone=client.phone,
        gender=client.gender if client.gender else None,
        day_of_birth=client.day_of_birth if client.day_of_birth else None,
        city=client.city if client.city else None,
        postcode=client.postcode if client.postcode else None,
        address=client.street if client.street else None,
        avatar=avatar_url,
        presentation=user_profile.presentation if user_profile.presentation else None,
    )


@router.patch("/my_profile", response={200: VolunteerUserProfileSchema, 400: dict, 404: dict}, tags=["Profile"])
def update_my_profile(request, profile_data: VolunteerProfileUpdateSchema):
    """
    Update current logged-in user's profile information.
    Allows partial updates of any field.
    """
    try:
        with transaction.atomic():
            client = Client.objects.get(user=request.user)

            user_profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'client': client}
            )

            if profile_data.first_name is not None:
                request.user.first_name = profile_data.first_name
            if profile_data.last_name is not None:
                request.user.last_name = profile_data.last_name
            if profile_data.email is not None:
                try:
                    validate_email(profile_data.email)
                except ValidationError:
                    return 400, {"error": "Ogiltigt e-postformat."}

                if User.objects.filter(email=profile_data.email).exclude(id=request.user.id).exists():
                    return 400, {"error": "E-postadressen är redan tagen av en annan användare."}
                
                request.user.email = profile_data.email
                request.user.username = profile_data.email
            
            # Update Client model fields
            if profile_data.phone is not None:
                client.phone = profile_data.phone
            if profile_data.gender is not None:
                client.gender = profile_data.gender
            if profile_data.day_of_birth is not None:
                client.day_of_birth = profile_data.day_of_birth
            if profile_data.city is not None:
                client.city = profile_data.city
            if profile_data.postcode is not None:
                client.postcode = profile_data.postcode
            if profile_data.address is not None:
                client.street = profile_data.address

            # Update UserProfile model fields
            if profile_data.presentation is not None:
                user_profile.presentation = profile_data.presentation

            request.user.save()
            client.save()
            user_profile.save()
            
            # Build avatar URL if avatar exists
            avatar_url = None
            if user_profile.avatar:
                avatar_url = user_profile.avatar.url
            
            return VolunteerUserProfileSchema(
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                email=request.user.email,
                phone=client.phone,
                gender=client.gender if client.gender else None,
                day_of_birth=client.day_of_birth,
                city=client.city if client.city else None,
                postcode=client.postcode if client.postcode else None,
                address=client.street if client.street else None,
                avatar=avatar_url,
                presentation=user_profile.presentation if user_profile.presentation else None,
            )
            
    except Client.DoesNotExist:
        return 404, {"error": "Användarprofilen hittades inte."}
    except Exception as e:
        return 400, {"error": "Fel uppstod när profilen uppdaterades."}


@router.post("/my_profile/avatar", response={200: dict, 400: dict, 404: dict}, tags=["Profile"])
def upload_avatar(request):
    try:
        client = Client.objects.get(user=request.user)

        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'client': client}
        )

        if 'avatar' not in request.FILES:
            return 400, {"error": "Ingen avatarfil tillhandahålls."}
        
        avatar_file = request.FILES['avatar']

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return 400, {"error": "Ogiltig filtyp. Endast JPEG, PNG, GIF och WebP är tillåtna."}

        max_size = 5 * 1024 * 1024  # 5MB
        if avatar_file.size > max_size:
            return 400, {"error": "Filen är för stor. Maximal storlek är 5 MB."}

        file_extension = os.path.splitext(avatar_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        if user_profile.avatar:
            try:
                if os.path.isfile(user_profile.avatar.path):
                    os.remove(user_profile.avatar.path)
            except (ValueError, OSError):
                pass

        user_profile.avatar.save(unique_filename, avatar_file, save=True)
        
        return 200, {
            "message": "Avataren har laddats upp",
            "avatar_url": user_profile.avatar.url
        }
        
    except Client.DoesNotExist:
        return 404, {"error": "Användarprofilen hittades inte."}
    except Exception as e:
        return 400, {"error": "Fel uppstod vid uppladdning av avatar."}


@router.post("/my_profile/change_password", response={200: dict, 400: dict}, tags=["Profile"])
def change_password(request, password_data: PasswordChangeSchema):
    try:
        user = authenticate(
            username=request.user.username,
            password=password_data.current_password
        )
        
        if not user:
            return 400, {"error": "Nuvarande lösenord är felaktigt."}
        
        # Validate new password
        if not password_data.new_password or len(password_data.new_password) < 8:
            return 400, {"error": "Det nya lösenordet måste vara minst 8 tecken långt."}
        
        # Set new password
        request.user.set_password(password_data.new_password)
        request.user.save()
        
        return 200, {"message": "Lösenordet har ändrats."}
        
    except Exception as e:
        return 400, {"error": "Fel vid ändring av lösenord."}


@router.delete("/my_profile", response={204: None, 400: dict, 404: dict}, tags=["Profile"])
def delete_my_profile(request):
    """
    This does not delete the user from the database but anonymizes all personal information.
    """
    try:
        with transaction.atomic():
            client = Client.objects.get(user=request.user)

            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = None

            request.user.first_name = "Anonymized"
            request.user.last_name = "User"
            request.user.email = f"anonymized_{request.user.id}@deleted.local"
            request.user.username = f"anonymized_{request.user.id}"
            request.user.is_active = False
            request.user.save()

            client.first_name = "Anonymized"
            client.last_name = "User"
            client.phone = "0000000000"
            client.email = f"anonymized_{request.user.id}@deleted.local"
            client.gender = ""
            client.street = ""
            client.postcode = ""
            client.city = ""
            client.country = ""
            client.day_of_birth = None
            client.personnr_lastnr = ""
            client.unokod = f"ANON_{request.user.id}"
            client.save()

            if user_profile:
                if user_profile.avatar:
                    try:
                        if os.path.isfile(user_profile.avatar.path):
                            os.remove(user_profile.avatar.path)
                    except (ValueError, OSError):
                        pass
                
                user_profile.avatar = None
                user_profile.presentation = "This profile has been anonymized"
                user_profile.save()
            
            return 204, None
            
    except Client.DoesNotExist:
        return 404, {"error": "Användarprofilen hittades inte."}
    except Exception as e:
        return 400, {"error": "Användarutloggning misslyckades."}
