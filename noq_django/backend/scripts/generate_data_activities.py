from faker import Faker
import random
from datetime import datetime, timedelta
from backend.models import Activity
from django.utils import timezone

def add_activities(nbr: int):
    faker = Faker("sv_SE")
    approved_options = [True, False]

    print("\n---- ACTIVITIES ----")

    current_activities = Activity.objects.count()
    if current_activities >= nbr:
        print(f"Det finns redan {current_activities} aktiviteter. Jag lägger inte till fler.")
        return

    while Activity.objects.count() < nbr:
        title = faker.sentence(nb_words=2).rstrip('.')
        description = faker.paragraph(nb_sentences=2)

        # Slumpmässig start- och sluttid
        naive_start = faker.date_time_between(start_date="-10d", end_date="+10d")
        start_time = timezone.make_aware(naive_start)
        duration_hours = random.randint(1, 48)
        end_time = start_time + timedelta(hours=duration_hours)

        is_approved = random.choice(approved_options)

        # Kontrollera att det inte finns någon dubbletttitel
        if Activity.objects.filter(title=title, start_time=start_time).exists():
            continue

        activity = Activity(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            is_approved=is_approved,
        )
        activity.save()
        print(f"Skapad: {title} ({start_time} → {end_time})")


def run(*args):
    docs = """
    generate test data
    
    python manage.py runscript generate_data _activities
    
    Args: [--script-args v2]
    
    """
    print(docs)
    add_activities(50)