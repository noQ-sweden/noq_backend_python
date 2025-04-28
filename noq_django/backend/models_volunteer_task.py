from django.db import models
from django.contrib.auth.models import User
from django.apps import apps


class VolunteerTask(models.Model):
  volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
  activity = models.ForeignKey("backend.Activity", on_delete=models.CASCADE, related_name="volunteer_tasks")
  
  STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
  ]
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
  assigned_at = models.DateTimeField(auto_now_add=True)

  def get_activity(self):
          Activity = apps.get_model("backend", "Activity")
          return Activity.objects.get(id=self.activity_id)


  def __str__(self):
    return f'{self.volunteer.username} - {self.activity.title} ({self.status})'
  