# https://django-extensions.readthedocs.io/en/latest/runscript.html

from  icecream import ic
import sys

from backend.models import Host, Reservation, User, Product, ProductRule, ProductBooking

def kontrollera(typ: str) -> bool:
    answer = input(f"Är du säker på att du vill ta bort alla {typ}?")
    if answer.lower() in ["q","quit"]:
        sys.exit()
    return answer.lower() in ["j","ja","y","yes"]

def count():
    ic(Reservation.objects.all().count())
    
    ic(ProductBooking.objects.all().count())
    ic(Product.objects.all().count())
    ic(ProductRule.objects.all().count())
    
    ic(Host.objects.all().count())
    ic(User.objects.all().count())
    

def run():
    
    count()

    if kontrollera("reservationer"):
        for rsrv in Reservation.objects.all():
            ic(rsrv, "borttagen")
            rsrv.delete()

    if kontrollera("bokningar"):
        for prd in ProductBooking.objects.all():
            prd.delete()
            ic(prd, "borttagen")
        
    if kontrollera("produkter"):
        for prd in Product.objects.all():
            prd.delete()
            ic(prd, "borttagen")

    if kontrollera("produktregler"):
        for prd in ProductRule.objects.all():
            prd.delete()
            ic(prd, "borttagen")

    if kontrollera("användare"):
        for user in User.objects.all():
            ic(user, "borttagen")
            user.delete()


    if kontrollera("härbärgen"):
        for host in Host.objects.all():
            ic(host, "borttagen")
            host.delete()

    count()
        
