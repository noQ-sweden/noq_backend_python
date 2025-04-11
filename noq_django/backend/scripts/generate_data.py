import random
from random import choice, sample
from datetime import datetime, timedelta
from django.utils import timezone
from icecream import ic
from faker import Faker
from django.contrib.auth.models import User, Group
import os
from django.conf import settings

from .delete_all_data import reset_all_data

from backend.models import Host, Client, Product, Region, Booking, BookingStatus, State, VolunteerProfile, VolunteerHostAssignment, Resource


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


""" 
def make_user(group: str, is_test_user: bool, first_name: str = None, last_name: str = None) -> User:
"""
def make_user(group: str, is_test_user: bool, first_name: str, last_name: str) -> User:
    faker = Faker("sv_SE")

    if is_test_user:
        password = "P4ssw0rd_for_Te5t+User"
        email = "user." + group + "@test.nu"
        first_name = "Test"
        last_name = group.capitalize()
    else:
        password = faker.password()
        email = faker.email()
        if first_name is None:
            first_name = faker.first_name()
        if last_name is None:
            last_name = faker.last_name()

    user = User.objects.create_user(username=email, password=password, first_name=first_name, last_name=last_name)
    group_obj, created = Group.objects.get_or_create(name=group)
    user.groups.add(group_obj)

    credentials_file = os.path.join(settings.BASE_DIR, 'backend', 'scripts', 'fake_credentials.txt')  # spara inloggningar till fil i testsyfte.
    with open(credentials_file, "a") as file:
        file.write(f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, Password: {password}, Group: {group}\n")

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

        new_user = make_user(group="host", is_test_user=is_test_user, first_name="Test" if is_test_user else faker.first_name(), last_name="Host" if is_test_user else faker.last_name())
        host.users.add(new_user)

        if is_test_user: is_test_user = False

        print(f"{host} i region {region} tillagd")

    return


def add_caseworkers(nbr: int) -> int:
    """ faker = Faker("sv_SE") """
    """ Assign caseworkers to hosts in the same region """

    print("\n---- CASEWORKERS ----")
    
    # Initialize the counter
    host_updated = 0
    
    caseworker_user = User.objects.filter(username="user.caseworker@test.nu").first()
    if not caseworker_user:
        caseworker_user = make_user(
            group="caseworker",
            is_test_user=True,
            first_name="Test",
            last_name="Caseworker",
            )

    # Fetch the user from 'user.host@test.nu' who manages the hosts
    host_user = User.objects.filter(username="user.host@test.nu").first()
    if not host_user:
        print("No user found for 'user.host@test.nu'. Cannot assign caseworkers.")
        return 0
    
    # Fetch all hosts managed by 'user.host@test.nu'
    hosts_managed_by_user = Host.objects.filter(users=host_user)
    

    for host in hosts_managed_by_user:
        hosts_in_region = Host.objects.filter(region=host.region)
        for region_host in hosts_in_region:
            region_host.caseworkers.add(caseworker_user)
            print(f"Assigned caseworker {caseworker_user.username} to host {region_host.name} in region {region_host.region.name}")
            host_updated += 1 # Increment the counter

    return host_updated

def add_volunteers(nbr: int) -> int:
    from random import choice, sample
    faker = Faker()
    print("\n---- VOLUNTEERS ----")
    volunteers_created = 0  

    availability_options = ["Weekdays", "Weekends", "Weekends-Evenings", "Weekends-Mornings", "Weekdays-Evenings", "Weekdays-Mornings"]
    skills_options = [
        "First aid", "Event coordination", "Fundraising", "Public speaking",
        "Data entry", "Teaching", "Translation", "Social media management"
    ]

    all_regions = list(Region.objects.all())
    all_hosts = list(Host.objects.all())

    # Check if the test volunteer user already exists
    test_user = User.objects.filter(username="user.volunteer@test.nu").first()
    
    if not test_user:
        # Create the test user if it doesn't exist
        test_user = make_user(
            group="volunteer",
            is_test_user=True,
            first_name="Test",
            last_name="Volunteer"
        )
        # Only create a VolunteerProfile if it doesn't already exist
        if not VolunteerProfile.objects.filter(user=test_user).exists():
            profile = VolunteerProfile.objects.create(
                user=test_user,
                availability=choice(availability_options),
                skills=", ".join(sample(skills_options, 2))
            )
            preferred_regions = sample(all_regions, choice([1, 2, 3]))
            profile.preferred_regions.set(preferred_regions)
            profile.save()

            # Assign an active host to the test volunteer
            assigned_host = choice(all_hosts)
            VolunteerHostAssignment.objects.create(
                volunteer=profile,
                host=assigned_host,
                active=True,
                start_date=timezone.now().date()
            )

        volunteers_created += 1

    # Calculate remaining volunteers to create
    additional_users_needed = nbr - volunteers_created
    for _ in range(additional_users_needed):
        # Generate random first and last names
        first_name = faker.first_name()
        last_name = faker.last_name()

        # Create a unique volunteer user
        volunteer_user = make_user(
            group="volunteer",
            is_test_user=False,
            first_name=first_name,
            last_name=last_name
        )

        if not VolunteerProfile.objects.filter(user=volunteer_user).exists():
            profile = VolunteerProfile.objects.create(
                user=volunteer_user,
                availability=choice(availability_options),
                skills=", ".join(sample(skills_options, 2))
            )

            preferred_regions = sample(all_regions, choice([1, 2, 3]))
            profile.preferred_regions.set(preferred_regions)
            profile.save()

            # Assign an active host to the volunteer
            assigned_host = choice(all_hosts)
            VolunteerHostAssignment.objects.create(
                volunteer=profile,
                host=assigned_host,
                active=True,
                start_date=timezone.now().date()
            )

            volunteers_created += 1

        print(f"Volunteer user created or updated: {volunteer_user.username}")

    print(f"\nTotal volunteers created: {volunteers_created}")
    return volunteers_created

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

        if Client.objects.filter(first_name=first_name, last_name=last_name).exists():
            continue

        last_edit = datetime.now() - timedelta(days=random.randint(0, 31))

        user = Client(
            user=make_user(group="user", is_test_user=is_test_user, first_name=first_name, last_name=last_name),
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

        if is_test_user: 
            is_test_user=False

def add_booking_statuses():
    statuses = [
        {"id": State.PENDING, "description": "pending"},
        {"id": State.DECLINED, "description": "declined"},
        {"id": State.ACCEPTED, "description": "accepted"},
        {"id": State.CHECKED_IN, "description": "checked_in"},
        {"id": State.IN_QUEUE, "description": "in_queue"},
        {"id": State.RESERVED, "description": "reserved"},
        {"id": State.CONFIRMED, "description": "confirmed"},
        {"id": State.ADVISED_AGAINST, "description": "advised_against"},
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
            client = Client.objects.get(id=user_id)
            date = datetime.now() + timedelta(days=random.randint(-1, days_ahead))
            end_date = date + timedelta(days=random.randint(1, 5))
            if verbose:
                print(f'{client} {date.strftime("%Y-%m-%d")}:')

            statuses_new = [State.PENDING, State.IN_QUEUE]

            if client:
                booking = Booking(
                    start_date=date,
                    end_date=end_date,
                    product=Product.objects.get(id=product_id),
                    user=client,
                    status=BookingStatus.objects.get(
                        id=statuses_new[random.randint(0, len(statuses_new) - 1)]
                    )
                )
                # We need to save initial status, otherwise availability
                # won't be correct
                booking.save()

                statuses_next = [
                    State.ACCEPTED,
                    State.RESERVED,
                    State.CONFIRMED,
                ]

                checked_in = (booking.start_date.date() <= datetime.now().date()) \
                    and (booking.end_date.date() >= datetime.now().date())

                if checked_in:  # this makes sure there are departures being generated
                    booking.status = BookingStatus.objects.get(id=State.CHECKED_IN)
                else:
                    booking.status = BookingStatus.objects.get(
                        id=statuses_next[random.randint(0, len(statuses_next) - 1)]
                    )

                booking.save()

            exceptions = 0
        except Exception as ex:
            exceptions += 1
            if verbose:
                print("Exception:", ex)
        else:
            print(
                f'Bokning tillagd {date.strftime("%Y-%m-%d")} {booking.product} för {booking.user.name()} {booking.product.host.region}, med Status {booking.status.description}'
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


def generate_resources(n=20):
    faker = Faker()
    applies_to_options = [["studies"], ["employment"], ["studies", "employment"]]
    target_groups = [
        "Children - under 18 years old",
        "Youth 18-25",
        "Adults 25+",
        "All ages",
    ]

    for _ in range(n):
        name = faker.company()
        opening_time = faker.time_object()
        closing_time = faker.time_object()
        if opening_time > closing_time:
            opening_time, closing_time = closing_time, opening_time

        Resource.objects.create(
            name=name,
            opening_time=opening_time,
            closing_time=closing_time,
            address=faker.address(),
            phone=faker.phone_number(),
            email=faker.email(),
            target_group=random.choice(target_groups),
            other=faker.sentence(),
            applies_to=random.choice(applies_to_options)
        )

    print(f"{n} resources created.")

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
    add_caseworkers(1)
    add_volunteers(2)
    add_products(6)
    add_users(16)

    add_booking_statuses()
    add_product_bookings(40, 7, v2_arg)

    generate_resources(20)
