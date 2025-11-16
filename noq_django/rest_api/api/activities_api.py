from ninja import Router, Query
from backend.models import Activity, VolunteerActivity
from datetime import datetime
from django.utils import timezone
from typing import List, Dict

router = Router(tags=["Activities"])

@router.get("/list")
def activities_list(request) -> List[Dict]:

    user = request.user
    now = timezone.now()

    activities = Activity.objects.filter(
        is_approved=True,
        start_time__gte=now
    ).order_by('start_time')

    registered_ids = set(
        VolunteerActivity.objects.filter(
            volunteer=user,
            activity__in=activities
        ).values_list("activity_id", flat=True)
    )

    return [{
        "id": a.id,
        "organization": a.organization,
        "activity_type": a.activity_type,
        "title": a.title,
        "description": a.description,
        "date": a.date.isoformat() if a.date else None,
        "start_time": a.start_time.isoformat(),
        "end_time": a.end_time.isoformat(),
        "contact_person": a.contact_person,
        "optional_instructions": a.optional_instructions,
        "is_registered": a.id in registered_ids
    } for a in activities]