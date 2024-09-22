from django.contrib.auth import authenticate, login
from ninja import NinjaAPI
from backend.models import (Host)

from .api_schemas import (
    LoginPostSchema,
    LoginSchema,
)


api = NinjaAPI(
    csrf=False,
    title="noQ API (Django Ninja API)",
)

api.add_router("/user/", "rest_api.api.user_api.router")
api.add_router("/host/", "rest_api.api.host_api.router")
api.add_router("/caseworker/", "rest_api.api.caseworker_api.router")
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