from ninja import Router
from backend.auth import group_auth
from backend.models import (Client)

router = Router(auth=lambda request: group_auth(request, "volunteer"))  # request defineras vid call, gruppnamnet är statiskt

@router.get("/clients", tags=["Volunteer"])
def clients(request):
    return {"status": "success"}, 200