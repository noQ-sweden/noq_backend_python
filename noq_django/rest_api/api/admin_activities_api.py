from ninja import Router, ModelSchema
from backend.models import Activity
from django.shortcuts import get_object_or_404

router = Router()

#---- API SCHEMAS ----#
class ActivitySchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["id", "title", "description", "start_time", "end_time", "is_approved"]

class ActivityCreateSchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["title", "description", "start_time", "end_time", "is_approved"]

class ActivityUpdateSchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["title", "description", "start_time", "end_time", "is_approved"]
#---- API ENDPOINTS ----#

@router.get("/", response=list[ActivitySchema], tags=["Admin Activities"])
def list_activities(request):
    return Activity.objects.all()

@router.post("/", response=ActivitySchema, tags=["Admin Activities"])
def create_activity(request, payload: ActivityCreateSchema):
    activity = Activity.objects.create(**payload.dict())
    return activity

@router.patch("/{activity_id}", response=ActivitySchema, tags=["Admin Activities"])
def update_activity(request, activity_id: int, payload: ActivityUpdateSchema):
    activity = get_object_or_404(Activity, id=activity_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(activity, attr, value)
    activity.save()
    return activity

@router.delete("/{activity_id}", tags=["Admin Activities"])
def delete_activity(request, activity_id: int):
    activity = get_object_or_404(Activity, id=activity_id)
    activity.delete()
    return {"success": True}