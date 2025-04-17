from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_volunteer_task import VolunteerTaskViewSet

router = DefaultRouter()
router.register(r'volunteer-tasks', VolunteerTaskViewSet)

urlpatterns = [
  path('api/', include(router.urls)),
]