from django.contrib.auth.models import User
from ninja.responses import JsonResponse

def group_auth(request, group): #Kolla så att användaren tillhör rätt grupp
    if not request.user.is_authenticated:
        return False
    
    if not request.user.groups.filter(name=group).exists():
        return False
    
    return True