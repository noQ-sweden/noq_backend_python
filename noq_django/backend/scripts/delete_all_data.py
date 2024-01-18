# https://django-extensions.readthedocs.io/en/latest/runscript.html

from  icecream import ic
import sys

from backend.models import Host, Reservation, User, Product, Region, ProductBooking

flag_all = False

def kontrollera(typ: str) -> bool:

    global flag_all    
    if flag_all:
        return True
    
    answer = input(f"Vill du ta bort alla {typ}(ja/nej/alla)?")
    if answer.lower() in ["q","quit"]:
        sys.exit()
    if answer.lower().startswith("a"):
        flag_all = True
    return answer.lower() in ["j","ja","y","yes"]

def count():
    ic(Reservation.objects.all().count())
    
    ic(ProductBooking.objects.all().count())
    ic(Product.objects.all().count())
    ic(Region.objects.all().count())
    
    ic(Host.objects.all().count())
    ic(User.objects.all().count())
    

def run():
    
    count()

    if kontrollera("reservationer"):
        for rsrv in Reservation.objects.all():
            ic(rsrv, "borttagen")
            rsrv.delete()

    if kontrollera("bokningar"):
        for booking in ProductBooking.objects.all():
            booking.delete()
            ic(booking, "borttagen")
        
    if kontrollera("regioner"):
        for region in Region.objects.all():
            region.delete()
            ic(region, "borttagen")

    if kontrollera("produkter"):
        for prd in Product.objects.all():
            prd.delete()
            print(prd, "borttagen")

    if kontrollera("användare"):
        for user in User.objects.all():
            ic(user, "borttagen")
            user.delete()


    if kontrollera("härbärgen"):
        for host in Host.objects.all():
            ic(host, "borttagen")
            host.delete()

    count()
        
