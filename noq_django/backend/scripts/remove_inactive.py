from datetime import datetime, timedelta
from icecream import ic

from backend.models import UserDetails

#Kolla om användaren har varit aktiv inom senaste X dagarna
def list_inactive():
    days_old = datetime.now() - timedelta(days=30) #Antal dagar innan flaggad för borttagning
    inactive_users = UserDetails.objects.filter(last_edit__lte=days_old)
    return inactive_users

def run():
    inactive_users = list_inactive()
    count = len(inactive_users)
    inactive_users.delete()
    print(f"Successfully removed {count}")