from ninja import NinjaAPI
from ninja.security import HttpBearer
from django.contrib.auth import authenticate, login

from .api_schemas import (
    LoginSchema,
)

api = NinjaAPI(
    csrf=False,
    title="noQ API (Django Ninja API)",
)

api.add_router("/user/", "noq_django.api.user_api.router")
api.add_router("/host/", "noq_django.api.host_api.router")
api.add_router("/so_admin/", "noq_django.api.admin_api.router")

#temporör testsektion
api.add_router("/test/", "noq_django.api.testing_api.router")

documentation = """

    Generell namnsättning för alla API:er
    
    /objects    GET     listar ett objekt, med metodnamn objects_list, kan även ha filterparametrar
    /objects/id GET     hämtar en unik instans av objekt(/objects/id), med metodnamn object_detail(id)
    /objects/id POST    skapar ett objekt, med metodnamn object_add
    /objects/id PATCH   uppdaterar ett objekt, med metodnamn object_update(id)
    /objects/id DELETE  tar bort ett objekt, med metodnamn object_delete(id)

"""

@api.post("/login/", tags=["Login"])
def login_user(request, payload: LoginSchema):
    username = payload.username
    password = payload.password
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return {"message": "Login Successful"}
    else:
        return {"message": "Login Failed"}, 401