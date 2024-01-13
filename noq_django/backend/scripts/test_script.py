# https://django-extensions.readthedocs.io/en/latest/runscript.html

from  icecream import ic

from backend.models import Host

def run():
    # Fetch all questions
    for h in Host.objects.all():
        ic(h)
        
        
