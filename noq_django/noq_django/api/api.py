from ninja import NinjaAPI
from ninja.security import HttpBearer
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group


from .api_schemas import (
    LoginPostSchema,
    LoginSchema,
)

api = NinjaAPI(
    csrf=False,
    title="noQ API (Django Ninja API)",
)

api.add_router("/user/", "noq_django.api.user_api.router")
api.add_router("/host/", "noq_django.api.host_api.router")
api.add_router("/so_admin/", "noq_django.api.admin_api.router")

# temporör testsektion
api.add_router("/old/", "noq_django.api.old_api.router")

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
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return LoginSchema(login_status = True, message = "Login Successful")
    else:
        return LoginSchema(login_status = False, message = "Login Failed")
