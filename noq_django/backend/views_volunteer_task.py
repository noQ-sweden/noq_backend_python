from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models_volunteer_task import VolunteerTask
from .serializers_volunteer_task import VolunteerTaskSerializer
from django.contrib.auth.models import User
from backend.models import Activity # Keeping the existing code intact

class VolunteerTaskViewSet(viewsets.ModelViewSet):
    queryset = VolunteerTask.objects.all()
    serializer_class = VolunteerTaskSerializer

    @action(detail=False, methods=['post'])
    def assign_task(self, request):
        """ 
        Assign a task to a volunteer

        """

        activity_id = request.data.get('activity_id')
        volunteer_id = request.data.get('volunteer_id')

        try:
            volunteer = User.objects.get(id=volunteer_id)
            activity = Activity.objects.get(id=activity_id)
            task, created = VolunteerTask.objects.get_or_create(volunteer=volunteer, activity=activity)

            if created:
                return Response({'message': 'Task assigned successfully'}, status=status.HTTP_201_CREATED)
            return Response({'message': 'Task already assigned'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=True, methods=['post'])
    def respons(self, request, pk=None):
        """
        Accept or reject a task
        """

        task = self.get_object()
        status_choice = request.data.get('status')

        if status_choice in ['accepted', 'rejected']:

          task.status = status_choice
          task.save()
          return Response({'message': f"Task {status_choice} successfully"}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid response'}, status=status.HTTP_400_BAD_REQUEST)