from ninja import Router, ModelSchema, Query
from backend.models import Activity, VolunteerActivity
from backend.auth import group_auth
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from ninja.responses import Response
from django.http import JsonResponse
from django.db.models import Q

router = Router()

#---- API ENDPOINTS ----#
@router.post("/signup/{activity_id}", tags=["Volunteer"])
def volunteer_activityes_signup(request, activity_id: int):
    user = request.user
    try:
        #activity = Activity.objects.get(id=activity_id, is_approved=True)
        activity = get_object_or_404(Activity, id=activity_id, is_approved=True)
        va, created = VolunteerActivity.objects.get_or_create(activity=activity, volunteer=user)
        if not created:
            return {"message": "You are already signed up for this activity."}
        return {"message": "You have successfully subscribed to the activity."}
    except Activity.DoesNotExist:
        return {'error': 'Activity not found or not approved.'}

@router.delete("/cancel/{activity_id}", tags=["Volunteer"])
def volunteer_activityes_cancel(request, activity_id: int):
    user = request.user
    try:
        activity = Activity.objects.get(id=activity_id)
        deleted, _ = VolunteerActivity.objects.filter(activity=activity, volunteer=user).delete()
        if deleted == 0:
            return {'message': 'You were not signed up for this activity.'}
        return {'message': 'You have successfully unsubscribed from the activity.'}
    except Activity.DoesNotExist:
        return {'error': 'No activity found.'}

@router.get("/list", tags=["Volunteer"])
def volunteer_activity_list(request):
    user = request.user

    volunteer_activities = VolunteerActivity.objects.filter(volunteer=user).select_related("activity")
    result = []

    for va in volunteer_activities:
        activity = va.activity
        result.append({
            "id": activity.id,
            "title": activity.title,
            "description": activity.description,
            "start_time": activity.start_time.isoformat(),
            "end_time": activity.end_time.isoformat(),
            "registered_at": va.registered_at.isoformat()
        })

    return result