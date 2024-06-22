import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker
from django.contrib.auth.models import User, Group

from .delete_all_data import reset_all_data

from backend.models import Host, Client, Product, Region, Booking, BookingStatus


def get_regioner():
    return [
        ["Göteborg", ["Göteborg", "Mölndal", "Hammarkullen"]],
        ["Farsta", ["Farsta", "Handen"]],
        ["Stockholm City", ["Stockholm", "Solna", "Sundbyberg"]],
        ["Skåne", ["Malmö", "Trelleborg", "Lund"]],
        ["Övriga landet", ["Umeå", "Sundsvall", "Örebro"]],
    ]


def get_region(index: int):
    list = get_regioner()
    return list[index][0]


def get_cities(index: int):
    list = get_regioner()
    return list[index][1]


def make_user(group: str, is_test_user: bool) -> User:  # användargrupp, användarnamn
    faker = Faker("sv_SE")
    if is_test_user:
        password = "P4ssw0rd_for_Te5t+User"
        email = "user." + group + "@test.nu"
    else:
        password = faker.password()
        email = faker.email()

    user = User.objects.create_user(username=email, password=password)
    group_obj, created = Group.objects.get_or_create(name=group)
    user.groups.add(group_obj)

    credentials_file = "backend/scripts/fake_credentials.txt"  # spara inloggningar till fil i testsyfte.
    with open(credentials_file, "a") as file:
        file.write(f"Email: {email}, Password: {password}, Group: {group}\n")

    return user


def add_region(nbr: int) -> int:
    print("\n---- REGION ----")

    if len(Region.objects.all()) >= nbr:
        return

    for region in get_regioner():
        region = Region(name=region[0])

        region.save()

        print(region, "tillagd")


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
    is_test_user: bool = True
    if User.objects.filter(username="user.host@test.nu").exists():
        is_test_user = False
        print("Test user exists already.")

    while len(Host.objects.all()) < nbr:
        ix = random.randint(0, len(härbärge) - 1)
        host_name = härbärge[ix]

        regioner = Region.objects.all()
        ix = random.randint(0, len(regioner) - 1)

        region = get_region(ix)
        region_obj = Region.objects.filter(name=region).first()

        if not region_obj:
            raise ValueError(f"Region is null! ({region} and {region_obj})")

        stad = random.choice(get_cities(ix))

        # Hoppa över om det är samma namn och stad
        if Host.objects.filter(name=host_name, city=stad).count() > 0:
            continue

        host = Host(
            name=host_name, street=faker.street_address(), city=stad, region=region_obj
        )

        host.save()

        new_user = make_user(group="host", is_test_user=is_test_user)
        host.users.add(new_user)

        if is_test_user: is_test_user = False

        print(f"{host} i region {region} tillagd")

    return


def add_users(nbr: int):
    faker = Faker("sv_SE")

    print("\n---- USERS ----")
    is_test_user: bool = True
    if User.objects.filter(username="user.user@test.nu").exists():
        is_test_user = False
        print("Test user exists already.")

    if len(Client.objects.all()) >= nbr:
        return

    while len(Client.objects.all()) < nbr:
        regioner = Region.objects.all()
        id = random.randint(0, len(regioner) - 1)

        gender = "M" if random.randint(0, 1) > 0 else "K"

        regioner = Region.objects.all()
        ix = random.randint(0, len(regioner) - 1)

        region = get_region(ix)
        region_obj = Region.objects.filter(name=region).first()

        if not region_obj:
            raise ValueError(f"Region is null! ({region} and {region_obj})")

        stad = random.choice(get_cities(ix))

        first_name: str = (
            faker.first_name_female() if gender == "K" else faker.first_name_male()
        )

        last_name: str = faker.last_name()

        if Client.objects.filter(first_name=first_name, last_name=last_name).values():
            continue

        last_edit = datetime.now() - timedelta(days=random.randint(0, 31))

        user = Client(
            user=make_user(group="user", is_test_user=is_test_user),
            first_name=first_name,
            last_name=last_name,
            region=region_obj,
            phone="070" + f"{random.randint(0,9)}-{random.randint(121212,909090)}",
            email=f"{first_name}.{last_name}@hotmejl.se".lower(),
            unokod=f"{random.randint(1000,9999)}",
            gender=gender,
            street=faker.street_address(),
            city=stad,
        )
        user.save(fake_data=last_edit)

        if is_test_user: is_test_user=False

def add_booking_statuses():
    statuses = [
        {"id": 1, "description": "pending"},
        {"id": 2, "description": "declined"},
        {"id": 3, "description": "accepted"},
        {"id": 4, "description": "checked_in"},
        {"id": 5, "description": "in_queue"},
        {"id": 6, "description": "reserved"},
        {"id": 7, "description": "confirmed"},
    ]

    for status in statuses:
        if not BookingStatus.objects.filter(id=status["id"]).exists():
            booking_status = BookingStatus.objects.create(
                id=status["id"], description=status["description"]
            )
            booking_status.save()
            print(
                f"BookingStatus '{status['description']}' created, ID {status['id']}."
            )
        else:
            print(f"BookingStatus with ID {status['id']} already exists.")


def add_product_bookings(nbr: int, days_ahead: int = 3, verbose: bool = False):
    faker = Faker("sv_SE")
    faker.seed_instance()
    max_exceptions = 20
    exceptions = 0

    print("\n---- PRODUCT BOOKINGS ----")

    product_min_id = Product.objects.order_by("id").first()
    user_min_id = Client.objects.order_by("id").first()

    while len(Booking.objects.all()) < nbr and exceptions < max_exceptions:
        product_id = product_min_id.id + random.randint(
            0, Product.objects.all().count() - 1
        )
        user_id = user_min_id.id + random.randint(0, Client.objects.all().count() - 5)

        try:
            brukare = Client.objects.get(id=user_id)
            datum = datetime.now() + timedelta(days=random.randint(-1, days_ahead))
            if verbose:
                print(f'{brukare} {datum.strftime("%Y-%m-%d")}:')

            if brukare:
                booking = Booking(
                    start_date=datum,
                    product=Product.objects.get(id=product_id),
                    user=brukare,
                )

                if (
                    booking.start_date.date()
                    == (datetime.now() - timedelta(days=1)).date()
                ):  # this makes sure there are departures being generaated
                    booking.status = BookingStatus.objects.get(id=4)
                else:
                    booking.status = BookingStatus.objects.get(id=random.randint(1, 4))

                booking.save()

            exceptions = 0
        except Exception as ex:
            exceptions += 1
            if verbose:
                print("Exception:", ex)
        else:
            print(
                f'Bokning tillagd {datum.strftime("%Y-%m-%d")} {booking.product} för {booking.user.name()} {booking.product.host.region}, med Status {booking.status.description}'
            )


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


def run(*args):
    docs = """
    generate test data
    
    python manage.py runscript generate_data 
    
    Args: [--script-args v2]
    
    """
    print(docs)
    v2_arg = "v2" in args

    if "reset" in args:
        reset_all_data()

    antal_hosts = len(Host.objects.all())
    antal_bookings = len(Host.objects.all())
    if antal_hosts > 0 or antal_bookings > 0:
        print("---- Tabellerna innehåller data -----")
        print("HOSTS:", antal_hosts, "BOOKINGS:", antal_bookings)
    add_region(5)
    add_hosts(10)
    add_products(6)
    add_users(16)

    add_booking_statuses()
    add_product_bookings(40, 7, v2_arg)
