from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ninja import NinjaAPI
from backend.models import (Host)
from ninja.responses import Response
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

from .api_schemas import (
    LoginPostSchema,
    LoginSchema,
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
api.add_router("/volunteer", "rest_api.api.volunteer_api.router")
api.add_router("/so_admin/", "rest_api.api.admin_api.router")

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


@api.post("/forgot-password/", tags=["Password Reset"])
def forgot_password(request, payload: ForgotPasswordSchema):

    try:
        user = User.objects.get(username=payload.username)
    except User.DoesNotExist:
        return JsonResponse({"status": False, "message": "User not found"}, status=404)
    
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    reset_link = f"http://localhost:5173/reset-password/{uidb64}/{token}/"

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