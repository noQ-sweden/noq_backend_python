from ninja import Router
from backend.models import Activity, VolunteerActivity
from django.shortcuts import get_object_or_404
from django.utils import timezone


router = Router()

#---- API ENDPOINTS ----#
@router.post("/signup/{activity_id}", tags=["Volunteer"])
def volunteer_activity_signup(request, activity_id: int):
    user = request.user
    activity = get_object_or_404(Activity, id=activity_id, is_approved=True)

    va, created = VolunteerActivity.objects.get_or_create(activity=activity, volunteer=user)
    return {
        "message": "Successfully registered." if created else "Already registered.",
        "activity": {
            "id": activity.id,
            "organization": activity.organization,
            "activity_type": activity.activity_type,
            "title": activity.title,
            "description": activity.description,
            "date": activity.date.isoformat() if activity.date else None,
            "start_time": activity.start_time.isoformat(),
            "end_time": activity.end_time.isoformat(),
            "contact_person": activity.contact_person,
            "optional_instructions": activity.optional_instructions,
            "is_registered": True
        }
    }

@router.delete("/cancel/{activity_id}", tags=["Volunteer"])
def volunteer_activity_cancel(request, activity_id: int):
    user = request.user
    activity = get_object_or_404(Activity, id=activity_id)

    deleted, _ = VolunteerActivity.objects.filter(activity=activity, volunteer=user).delete()
    return {
        "message": "Successfully deregistered." if deleted else "You were not registered.",
        "activity": {
            "id": activity.id,
            "organization": activity.organization,
            "activity_type": activity.activity_type,
            "title": activity.title,
            "description": activity.description,
            "date": activity.date.isoformat() if activity.date else None,
            "start_time": activity.start_time.isoformat(),
            "end_time": activity.end_time.isoformat(),
            "contact_person": activity.contact_person,
            "optional_instructions": activity.optional_instructions,
            "is_registered": False
        }
    }

@router.get("/list", tags=["Volunteer"])
def volunteer_activity_list(request):
    user = request.user
    volunteer_activities = VolunteerActivity.objects.filter(volunteer=user).select_related("activity")
    result = []

    for va in volunteer_activities:
        a = va.activity
        result.append({
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
            "registered_at": va.registered_at.isoformat(),
            "is_registered": True
        })
    return result