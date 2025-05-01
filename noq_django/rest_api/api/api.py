from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from ninja import NinjaAPI
from backend.models import (Host, Client, Region)
from django.contrib.auth.models import User, Group
from ninja.responses import Response
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.core.mail import send_mail
from django.conf import settings
import os

from .api_schemas import (
    LoginPostSchema,
    LoginSchema,
    UserRegistrationSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)

api = NinjaAPI(
    csrf=False,
    title="noQ API (Django Ninja API)",
)

api.add_router("/user/", "rest_api.api.user_api.router")
api.add_router("/host/", "rest_api.api.host_api.router")
api.add_router("/caseworker/", "rest_api.api.caseworker_api.router")
api.add_router("/activities", "rest_api.api.activities_api.router")
api.add_router("/volunteer", "rest_api.api.volunteer_api.router")
api.add_router("/volunteer/activities", "rest_api.api.volunteer_activities_api.router")
api.add_router("/so_admin/", "rest_api.api.admin_api.router")
api.add_router("/admin/activities", "rest_api.api.admin_activities_api.router")
api.add_router("/admin/volunteer", "rest_api.api.admin_volunteer_api.router")


# temporör testsektion
api.add_router("/old/", "rest_api.api.old_api.router")

documentation = """
    Generell namnsättning för alla API:er
    
    /objects    GET     listar ett objekt, med metodnamn objects_list, kan även ha filterparametrar
    /objects/id GET     hämtar en unik instans av objekt(/objects/id), med metodnamn object_detail(id)
    /objects/id POST    skapar ett objekt, med metodnamn object_add
    /objects/id PATCH   uppdaterar ett objekt, med metodnamn object_update(id)
    /objects/id DELETE  tar bort ett objekt, med metodnamn object_delete(id)
"""

@login_required
@api.get("/self/auth/", response=LoginSchema, tags=["Login"])
def get(request):
    if not request.user.is_authenticated:
        return JsonResponse({"login_status": False, "message": "User not authenticated"}, status=401)

    user_groups = [g.name for g in request.user.groups.all()]
    host = None

    if "host" in user_groups:
        try:
            host = Host.objects.get(users=request.user)
        except Host.DoesNotExist:
            pass

    return LoginSchema(
        login_status=True,
        message="Login Successful",
        groups=user_groups,
        host=host,
        first_name=request.user.first_name,
        last_name=request.user.last_name 
    )


@login_required
@api.get("/logout/", tags=["Login"])
def logout_user(request):
    logout(request)
    response =  JsonResponse({"login_status": False, "message": "Logout Successful"}, status=200)
    response.delete_cookie("sessionid")
    return response


@api.post("/login/", response=LoginSchema, tags=["Login"])
def login_user(request, payload: LoginPostSchema):
        
    email = payload.email
    password = payload.password
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        user_groups = [g.name for g in request.user.groups.all()]
        host = None

        if "host" in user_groups:
            try:
                host = Host.objects.get(users=user)
            except Host.DoesNotExist:
                pass

        # Add firt_name and last_name to the response        
        return LoginSchema(
            login_status=True,
            message="Login Successful",
            groups=user_groups,
            host=host,
            first_name=user.first_name, # Include users first_name 
            last_name=user.last_name # Include users last_name
        )
    else:
        return LoginSchema(
            login_status=False,
            message="Login Failed",
            groups=None,
            host=None,
            first_name=None,
            last_name=None
        )


@api.post("/register/", response={201: dict, 400: dict}, tags=["Login"])
def register_user(request, user_data: UserRegistrationSchema):
    role = request.headers.get("X-User-Role", "user")
    allowed_roles = ["user", "volunteer"]
    if role not in allowed_roles:
        return 400, {"error": "Invalid role specified."}

    if not user_data.email or not user_data.email.strip():
        return 400, {"error": "E-post måste anges och får inte vara tom."}
    try:
        validate_email(user_data.email)
    except ValidationError:
        return 400, {"error": "Ogiltig e-postadress."}

    if not user_data.password or not user_data.password.strip():
        return 400, {"error": "Lösenord måste anges och får inte vara tomt."}

    if User.objects.filter(email=user_data.email).exists():
        return 400, {"error": "Användare med denna e-postadress finns redan."}

    try:
        with transaction.atomic():
            region_obj = Region.objects.first()
            if not region_obj:
                raise ValueError("Regionen finns inte i databasen.")
            
            # Create the user account
            userClient = User.objects.create_user(
                email=user_data.email,
                username=user_data.email,
                password=user_data.password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                is_active=False,
            )

            group_obj, _ = Group.objects.get_or_create(name=role)
            userClient.groups.add(group_obj)

            # Create the Client record
            client = Client(
                user=userClient,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                region=region_obj,
                phone="",
                email=user_data.email,
                gender="",
                street="",
                postcode="",  
                city="",
                country="",
                day_of_birth=None,
                personnr_lastnr="",
                unokod="",
            )
            client.save()

            uidb64 = urlsafe_base64_encode(force_bytes(userClient.pk))
            token = default_token_generator.make_token(userClient)
            activation_path = f"{uidb64}/{token}"
            activation_link = settings.FRONTEND_URL + activation_path

            subject = "Välkommen till NoQ – aktivera ditt konto"
            message = (
                f"Hej {user_data.first_name},\n\n"
                "Välkommen till NoQ!\n\n För att komma igång och logga in, "
                "måste du aktivera ditt konto genom att klicka på länken nedan:\n\n"
                f"{activation_link}\n\n"
                "Med vänliga hälsningar,\n"
                "NoQ-teamet"
            )

            # Send email after registration
            send_mail(
                subject,           
                message,          
                None,            
                [user_data.email],
                fail_silently=False,
            )

    except IntegrityError:
        return 400, {"error": "Något gick fel: En användare kunde inte skapas."}
    except ValueError:
        return 400, {"error": "Ett oväntat fel inträffade. Vänligen försök igen."}
    except Exception:
        return 400, {"error": "Ett oväntat fel inträffade. Vänligen försök igen."}
    return 201, {"success": "Användare registrerad! – kolla mejlen för aktivering", "user_id": userClient.id}


@api.post("/activate/{uidb64}/{token}/", response={200: dict, 400: dict})
def activate_account(request, uidb64: str, token: str):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return 400, {"error": "Ogiltig aktiveringslänk."}
    
    if user.is_active:
        return 400, {"error": "Länken är ogiltig eller har gått ut."}

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return 200, {"message": "Konto aktiverat."}
    else:
        return 400, {"error": "Länken är ogiltig eller har gått ut."}
    return 201, {"success": "Användare registrerad!", "user_id": userClient.id}


@api.post("/forgot-password/", tags=["Password Reset"])
def forgot_password(request, payload: ForgotPasswordSchema):

    try:
        user = User.objects.get(username=payload.username)
    except User.DoesNotExist:
        return JsonResponse({"status": False, "message": "User not found"}, status=404)
    
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    reset_url_base = os.getenv("RESET_LINK")
    reset_link = f"{reset_url_base}/{uidb64}/{token}/"

    send_mail(
        "Password Reset Request",
        f"Click the link to reset your password: {reset_link}",
        settings.DEFAULT_FROM_EMAIL,
        [user.username],
        fail_silently=False,
    )
    return JsonResponse({"status": True, "message": "Password reset link sent to email"}, status=200)

@api.post("/reset-password/", tags=["Password Reset"])
def reset_password(request, payload: ResetPasswordSchema):
    try:
        uid = urlsafe_base64_decode(payload.uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, payload.token):
        user.set_password(payload.new_password)
        user.save()
        return JsonResponse({"status": True, "message": "Password reset successful"}, status=200)
    else:
        return JsonResponse({"status": False, "message": "Invalid token"}, status=400)
