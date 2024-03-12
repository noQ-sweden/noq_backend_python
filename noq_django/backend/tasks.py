from datetime import datetime, timedelta
from icecream import ic

from backend.models import UserDetails

#Lägg i denna fil till funktioner som skall köras som bakrundsprocesser genom django-q
#skapa sedan processen genom adminsidan /admin/django_q/schedule/ eller lägg till dem i generate_jobs.py scriptet

#Kolla om användaren har varit aktiv inom senaste X dagarna
def remove_inactive():
    days_old = datetime.now() - timedelta(days=30) #Antal dagar innan flaggad för borttagning
    inactive_users = UserDetails.objects.filter(last_edit__lte=days_old)
    count = len(inactive_users)
    inactive_users.delete()
    print(f"Successfully removed {count}")