from datetime import date
from typing import Dict, List
from ninja import Router, ModelSchema, Schema
from backend.models import Activity, VolunteerActivity, VolunteerProfile
from django.shortcuts import get_object_or_404

from .api_schemas import ActivityUpdateSchema

router = Router()

#---- API SCHEMAS ----#
class ActivitySchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["id", "title", "description", "start_time", "end_time", "is_approved"]

class VolunteerProfileSchema(Schema):
    id: int
    first_name: str
    last_name: str
    email: str
    date_joined: date
    registered_at: date

class ActivityDetailSchema(ActivitySchema):
    volunteers: List[VolunteerProfileSchema]

class ActivityCreateSchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["title", "description", "start_time", "end_time", "is_approved"]

class ActivityUpdateSchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["title", "description", "start_time", "end_time", "is_approved"]
#---- API ENDPOINTS ----#

# List all activities without volunteers' detail
@router.get("/", response=list[ActivitySchema], tags=["Admin Activities"])
def list_activities(request):
    return Activity.objects.all()

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