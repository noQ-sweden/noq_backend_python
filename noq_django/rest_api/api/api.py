from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ninja import NinjaAPI
from backend.models import (Host, Client, Region)
from django.contrib.auth.models import User, Group
from ninja.responses import Response
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings

from .api_schemas import (
    LoginPostSchema,
    LoginSchema,
    UserRegistrationSchema,
)

api = NinjaAPI(
    csrf=False,
    title="noQ API (Django Ninja API)",
)

api.add_router("/user/", "rest_api.api.user_api.router")
api.add_router("/host/", "rest_api.api.host_api.router")
api.add_router("/caseworker/", "rest_api.api.caseworker_api.router")
api.add_router("/volunteer", "rest_api.api.volunteer_api.router")
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
                last_name=user_data.last_name
            )

            group_obj, _ = Group.objects.get_or_create(name=role)
            userClient.groups.add(group_obj)

            # Create the Client record
            user = Client(
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
            user.save()

            # Send email after registration
            send_mail(
                "Välkommen till noQ!",
                f"Hej {user_data.first_name},\n\nVälkommen till noQ! Ditt konto har nu skapats och du kan logga in med din e-postadress.",
                None,  # Use default email from settings
                [user_data.email],
                fail_silently=False,
            )

    except IntegrityError:
        return 400, {"error": "Något gick fel: En användare kunde inte skapas."}
    except ValueError:
        return 400, {"error": "Ett oväntat fel inträffade. Vänligen försök igen."}
    except Exception:
        return 400, {"error": "Ett oväntat fel inträffade. Vänligen försök igen."}

    return 201, {"success": "Användare registrerad!", "user_id": userClient.id}