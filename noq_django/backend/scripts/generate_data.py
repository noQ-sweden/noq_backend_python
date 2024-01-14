import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, User, Reservation, Room


def add_hosts(nbr: int) -> int:
    faker = Faker("sv_SE")

    härbärge = [
        "Korskyrkan",
        "Grimmans Akutboende",
        "Stadsmissionen",
        "gemenskap",
        "Bostället",
    ]

    print("\n---- HOSTS ----")
    
    while len(Host.objects.all())<nbr:
        city=faker.city()
        id = random.randint(0,len(härbärge)-1)
        ic(id)
        host_name = härbärge[id]
        
        if Host.objects.filter(name=host_name, city=city).values():
            continue
        
        host = Host(
            name=host_name,
            street=faker.street_address(),
            city=faker.city(),
            total_available_places=random.randint(1,4),
        )

        host.save()

        ic(host, "added")

    return

def add_users(nbr: int):
    faker = Faker("sv_SE")

    print("\n---- USERS ----")
    if len(User.objects.all())>=nbr:
        return
    
    while len(User.objects.all())<nbr:
        
        
        gender = "M" if random.randint(0, 1) > 0 else "F"
        
        first_name:str = str(faker.first_name_female()) if gender == "M" else str(faker.first_name_male())
        last_name:str = str(faker.last_name()),
        
        if User.objects.filter(first_name=first_name, last_name=last_name).values():
            continue
        
        user = User(
            first_name=first_name,
            last_name = last_name,
            phone="070" + f"{random.randint(0,9)}-{random.randint(121212,909090)}",
            email=f'{first_name}.{last_name}@hotmejl.se',
            unokod=f"{random.randint(1000,9999)}",
            gender = gender
        )
        user.save()

def add_reservations(nbr: int, days_ahead: int=3):
    faker = Faker("sv_SE")
    faker.seed_instance()
    max_exceptions = 20
    exceptions = 0

    print("\n---- RESERVATION ----")
    
    host_1st = Host.objects.order_by("id").first()
    user_1st = User.objects.order_by("id").first()
    
    while len(Reservation.objects.all())<nbr and exceptions < max_exceptions :
        host_id = host_1st.id + random.randint(0, Host.objects.all().count() - 3)
        user_id = user_1st.id + random.randint(0, User.objects.all().count() - 5)
        
        ic(host_id, user_id)
        reservation = Reservation(
            start_date=datetime.now() + timedelta(days=random.randint(1, days_ahead)),
            
            host=Host.objects.get(id=host_id),
            user=User.objects.get(id=user_id),
        )
        
        try:
            reservation.save()
            exceptions = 0
        except Exception as ex:
            ic(ex, reservation)
            exceptions += 1
        else:
            print("User reservation added")


def run():
    add_hosts(7)
    add_users(12)
    add_reservations(40, 7)
