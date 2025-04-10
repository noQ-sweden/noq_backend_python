from ninja import Router, Query
from backend.models import Activity, VolunteerActivity
from datetime import datetime
from django.utils.timezone import make_aware

router = Router(tags=["Activities"])

@router.get("/list")
def activities_list(request, date: str = Query(..., description="Date in YYYY-MM-DD format")):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        start_of_day = make_aware(datetime.combine(date_obj, datetime.min.time()))
        end_of_day = make_aware(datetime.combine(date_obj, datetime.max.time()))
    except Exception:
        return {"error": "Invalid date format"}

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