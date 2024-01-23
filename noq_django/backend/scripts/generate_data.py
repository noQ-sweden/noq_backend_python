import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, User, Product, Region, Booking


def add_region(nbr: int) -> int:
    regioner = [
        "Farsta",
        "Stockholm City",
        "Göteborg",
        "Skåne",
        "Övriga landet",
    ]

    print("\n---- REGION ----")

    if len(Region.objects.all()) >= nbr:
        return

    for namn in regioner:
        region = Region(region_name=namn)

        region.save()

        ic(region, "added")


def add_hosts(nbr: int) -> int:
    faker = Faker("sv_SE")

    härbärge = [
        "Korskyrkan",
        "Grimmans Akutboende",
        "Stadsmissionen",
        "Ny gemenskap",
        "Bostället",
    ]

    print("\n---- HOSTS ----")

    while len(Host.objects.all()) < nbr:
        city = faker.city()
        id = random.randint(0, len(härbärge) - 1)
        host_name = härbärge[id]

        # Hoppa över om det är samma namn och stad
        if Host.objects.filter(host_name=host_name, city=city).values():
            continue

        regioner = Region.objects.all()
        id = random.randint(0, len(regioner) - 1)

        host = Host(
            host_name=host_name,
            street=faker.street_address(),
            city=faker.city(),
            region=regioner[id],
            total_available_places=random.randint(1, 4),
        )

        host.save()

        ic(host, "added")

    return


def add_users(nbr: int):
    faker = Faker("sv_SE")

    print("\n---- USERS ----")
    if len(User.objects.all()) >= nbr:
        return

    while len(User.objects.all()) < nbr:
        
        regioner = Region.objects.all()
        id = random.randint(0, len(regioner) - 1)

        gender = "M" if random.randint(0, 1) > 0 else "K"

        first_name: str = (
            faker.first_name_female() if gender == "K" else faker.first_name_male()
        )

        last_name: str = faker.last_name()

        if User.objects.filter(first_name=first_name, last_name=last_name).values():
            continue

        user = User(
            first_name=first_name,
            last_name=last_name,
            region = regioner[id],
            phone="070" + f"{random.randint(0,9)}-{random.randint(121212,909090)}",
            email=f"{first_name}.{last_name}@hotmejl.se".lower(),
            unokod=f"{random.randint(1000,9999)}",
            gender=gender,
            street=faker.street_address(),
            city=faker.city(),
        )
        user.save()


def add_product_bookings(nbr: int, days_ahead: int = 3):
    faker = Faker("sv_SE")
    faker.seed_instance()
    max_exceptions = 20
    exceptions = 0

    print("\n---- PRODUCT BOOKINGS ----")

    product_min_id = Product.objects.order_by("id").first()
    user_min_id = User.objects.order_by("id").first()

    while len(Booking.objects.all()) < nbr and exceptions < max_exceptions:
        product_id = product_min_id.id + random.randint(
            0, Host.objects.all().count() - 3
        )
        user_id = user_min_id.id + random.randint(0, User.objects.all().count() - 5)

        booking = Booking(
            start_date=datetime.now() + timedelta(days=random.randint(1, days_ahead)),
            product=Product.objects.get(id=product_id),
            user=User.objects.get(id=user_id),
        )

        try:
            booking.save()
            exceptions = 0
        except Exception as ex:
            exceptions += 1
        else:
            print("Booking added")


def add_products(nbr: int = 3):
    for host in Host.objects.all():
        places = random.randint(2, 6)
        if not Product.objects.filter(host=host, name="rum"):
            rum = Product.objects.create(
                name="room",
                description=f"{places}-bäddsrum",
                total_places=places,
                host=host,
                type="room",
            )

        woman_only = Product.objects.create(
            name="woman-only",
            description=f"{places}-bäddsrum för kvinnor",
            total_places=places,
            host=host,
            type="woman-only",
        )


def run():
    add_region(5)
    add_hosts(7)
    add_products(2)
    add_users(12)
    add_product_bookings(40, 7)
