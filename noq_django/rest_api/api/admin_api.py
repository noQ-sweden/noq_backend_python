from ninja import Router

from backend.auth import group_auth


router = Router(auth=lambda request: group_auth(request, "so_admin")) #request defineras vid call, gruppnamnet är statiskt