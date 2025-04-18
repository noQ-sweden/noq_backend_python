# rest_api/api/admin_volunteer_api.py
from ninja import Router, Schema
from backend.models import VolunteerTask
from backend.auth import group_auth
from django.shortcuts import get_object_or_404

router = Router()

#---- API SCHEMAS ----#
class TaskStatusSchema(Schema):
    status: str

@router.get("/tasks", response=list, tags=["Admin Volunteer"])
def get_available_tasks(request):
    tasks = VolunteerTask.objects.select_related("volunteer", "activity").all()

    return [
        {
            "id": task.id,
            "volunteer": task.volunteer.username,
            "activity_title": task.activity.title,
            "status": task.status,
            "assigned_at": task.assigned_at,
        }
        for task in tasks
    ]

@router.patch("/tasks/{task_id}", tags=["Admin Volunteer"])
def update_task_status(request, task_id: int, payload: TaskStatusSchema):
    task = get_object_or_404(VolunteerTask, id=task_id)
    task.status = payload.status
    task.save()
    return {"status": task.status}