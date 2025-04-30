from ninja import Router, Query
from backend.models import Activity, VolunteerActivity
from datetime import datetime
from django.utils.timezone import make_aware
from typing import List, Dict

router = Router(tags=["Activities"])

def parse_date(date_str: str) -> (datetime, datetime): # type: ignore
    """
    Parses a date string in YYYY-MM-DD format and returns the start and end of the day.
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_of_day = make_aware(datetime.combine(date_obj, datetime.min.time()))
        end_of_day = make_aware(datetime.combine(date_obj, datetime.max.time()))
        return start_of_day, end_of_day
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

@router.get("/list")
def activities_list(request, date: str = Query(..., description="Date in YYYY-MM-DD format")) -> List[Dict]:
    
    try:
        start_of_day, end_of_day = parse_date(date)
    except ValueError as e:
        return {"error": str(e)}

    user = request.user

    activities = Activity.objects.filter(
        is_approved=True,
        start_time__gte=start_of_day,
        start_time__lte=end_of_day
    )

    registered_ids = set(
        VolunteerActivity.objects.filter(
            volunteer=user,
            activity__in=activities
        ).values_list("activity_id", flat=True)
    )

    return [{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "start_time": a.start_time.isoformat(),
        "end_time": a.end_time.isoformat(),
        "is_registered": a.id in registered_ids
    } for a in activities]