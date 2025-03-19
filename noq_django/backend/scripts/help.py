import random
from datetime import datetime, timedelta
from icecream import ic
from faker import Faker

from backend.models import Host, Client, Product, Region, Booking, Available


def commands_list():
    docs = """
    Scripts:
    host        Alla härbärgen och deras bokningar
    user        Alla brukare och deras bokningar
    available   Alla tillgängliga rum de närmaste dagarna
    
    booking     Alla bokningar
    
    test_book   Test av bokning
    
    generate_data   Generera testdata
    delete_all_data Rensa all testdata
    """
    print(docs)


def run():
    commands_list()
    # available_list()
