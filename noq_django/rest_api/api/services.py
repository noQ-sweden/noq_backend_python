from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from backend.models  import UserProfile

def update_user_profile(user_id, data):
    """
    Safely updates a UserProfile with validated foreign keys.

    :param user_id: int – the user ID (primary key in User)
    :param data: dict – fields to update on the UserProfile
    :return: UserProfile instance
    """
    try:
        # Validate and get the main user
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValidationError(f"User with ID {user_id} does not exist.")

    try:
        # Get or create the profile (optional: only update if it exists)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Optional: validate and set supporting_person
        supporting_person_id = data.get("supporting_person_id")
        if supporting_person_id:
            try:
                supporting_person = User.objects.get(id=supporting_person_id)
                profile.supporting_person = supporting_person
            except User.DoesNotExist:
                raise ValidationError(f"Supporting user with ID {supporting_person_id} does not exist.")
        else:
            profile.supporting_person = None  # Clear it if not provided

        # Update other fields
        profile.first_name = data.get("first_name", profile.first_name)
        profile.last_name = data.get("last_name", profile.last_name)
        profile.sex = data.get("sex", profile.sex)
        profile.birthday = data.get("birthday", profile.birthday)
        profile.birth_year = data.get("birth_year", profile.birth_year)
        profile.email = data.get("email", profile.email)
        profile.telephone = data.get("telephone", profile.telephone)
        profile.language = data.get("language", profile.language)
        profile.presentation = data.get("presentation", profile.presentation)
        profile.avatar = data.get("avatar", profile.avatar)  # If handling images, be careful here

        profile.save()
        return profile

    except Exception as e:
        raise ValidationError(f"Error updating user profile: {str(e)}")
