from typing import List
from ninja import Router
from backend.models import Activity, VolunteerActivity
from django.shortcuts import get_object_or_404

from .api_schemas import ActivityUpdateSchema


from .api_schemas import (
    ActivitySchema,
    ActivityDetailSchema,
    ActivityCreateSchema,
    ActivityUpdateSchema,
    ActivityListSchema
)

#TODO This needs to be changed !!!!!!!!
router = Router()


# List all activities without volunteers' detail
@router.get("/", response=List[ActivityListSchema], tags=["Admin Activities"])
def list_activities(request):
    activities = Activity.objects.all()
    result = []
    for activity in activities:
        tasks = VolunteerActivity.objects.filter(activity_id=activity.id).select_related("volunteer")
        volunteers = [
            {
                "id": task.volunteer.id,
                "first_name": task.volunteer.first_name,
                "last_name": task.volunteer.last_name,
            }
            for task in tasks
        ]
        result.append({
            "id": activity.id,
            "title": activity.title,
            "description": activity.description,
            "start_time": activity.start_time,
            "end_time": activity.end_time,
            "is_approved": activity.is_approved,
            "volunteers": volunteers
        })
    return result


# Get details with volunteers' info of a specific activity by ID
@router.get("/{activity_id}", response=ActivityDetailSchema, tags=["Admin Activities"])
def activity_detail(request, activity_id: int):
    activity = get_object_or_404(Activity, id=activity_id)
    tasks = VolunteerActivity.objects.filter(activity_id=activity_id).select_related("volunteer")
    volunteers = [
        {
            "id": task.volunteer.id,
            "first_name": task.volunteer.first_name,
            "last_name": task.volunteer.last_name,
            "email": task.volunteer.email,
            "date_joined": task.volunteer.date_joined.date(),
            "registered_at": task.registered_at.date()
        }
        for task in tasks
    ]

    return {
        **ActivitySchema.from_orm(activity).dict(),
        "volunteers": volunteers
    }

# Add an activity
@router.post("/", response=ActivitySchema, tags=["Admin Activities"])
def create_activity(request, payload: ActivityCreateSchema):
    activity = Activity.objects.create(**payload.dict())
    return activity

# Update detail of activity
@router.patch("/{activity_id}", response=ActivitySchema, tags=["Admin Activities"])
def update_activity(request, activity_id: int, payload: ActivityUpdateSchema):
    activity = get_object_or_404(Activity, id=activity_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(activity, attr, value)
    activity.save()
    return activity

# Delete an activity
@router.delete("/{activity_id}", tags=["Admin Activities"])
def delete_activity(request, activity_id: int):
    activity = get_object_or_404(Activity, id=activity_id)
    activity.delete()
    return {"success": True}
