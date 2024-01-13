import random
from typing import List
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import func, table, column
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, User, Reservation, Room


def add_hosts() -> int:
    faker = Faker("sv_SE")

    härbärge = [
        "x Korskyrkan",
        "x Grimmans Akutboende",
        "x Stadsmissionen",
        "Ny gemenskap",
        "Bostället",
    ]

    print("\n---- HOSTS ----")
    if len(Host.objects.all().values())>=len(härbärge):
        return

    for i in range(2):
        host = Host(
            name=härbärge[i],
            street=faker.street_address(),
            city=faker.city(),
            count_of_available_places=i * 2 + 1,
            total_available_places=i * 2 + 1,
        )

        host.save()

        ic(host.id, host.name, "added")

    return i + 1

def run():
    add_hosts()
    print("OK")
