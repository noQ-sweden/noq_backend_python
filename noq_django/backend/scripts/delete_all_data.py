# https://django-extensions.readthedocs.io/en/latest/runscript.html

from icecream import ic
import sys

from backend.models import Host, User, Product, Region, Booking, Available

flag_all = False


def kontrollera(typ: str) -> bool:
    global flag_all
    if flag_all:
        print(f"Tar bort alla {typ}")
        return True

    answer = input(f"Vill du ta bort alla {typ}(ja/nej/alla)?")
    if answer.lower() in ["q", "quit"]:
        sys.exit()
    if answer.lower().startswith("a"):
        flag_all = True
    return answer.lower() in ["j", "ja", "y", "yes"]


def count():
    ic(Available.objects.all().count())
    ic(Booking.objects.all().count())
    ic(Product.objects.all().count())
    ic(Region.objects.all().count())

    ic(Host.objects.all().count())
    ic(User.objects.all().count())


def run():
    count()

    if kontrollera("bokningar"):
        for booking in Booking.objects.all():
            booking.delete()
            ic(booking, "borttagen")

    if kontrollera("regioner"):
        for region in Region.objects.all():
            region.delete()
            ic(region, "borttagen")

    if kontrollera("tillgängliga produkter"):
        for prd in Available.objects.all():
            prd.delete()
            print(prd, "borttagen")

    if kontrollera("bokningar"):
        for prd in Booking.objects.all():
            prd.delete()
            print(prd, "borttagen")

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
