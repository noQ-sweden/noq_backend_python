from datetime import datetime
from django_q.models import Schedule


def delete_entries(): #rensa tidigare schemaläggningar från databasen om det finns några
    jobs = Schedule.objects.all()
    if len(jobs) != 0:
        for i in jobs:
            i.delete()
    

def create_jobs(): #lägg till bakrundsprocesser som skall skapas här
    Schedule.objects.create(
    name='Remove Inactive Users',
    func='backend.tasks.remove_inactive',
    schedule_type=Schedule.DAILY,
    repeats=-1,
    next_run=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
    )

def run():
    delete_entries()
    create_jobs()