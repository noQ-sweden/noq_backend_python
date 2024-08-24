from ninja import Router
from ninja.errors import HttpError
from django.http import HttpResponse
from backend.auth import group_auth

router = Router(auth=lambda request: group_auth(request, "caseworker"))  # request defineras vid call, gruppnamnet är statiskt

# api/caseworker/ returns the host information
@router.get("/", response=str, tags=["caseworker-frontpage"])
def get_caseworker_data(request):
    try:
        return HttpResponse("Caseworker frontpage data comes here...", status=200)
    except:
        raise HttpError(200, "User is not a caseworker.")
