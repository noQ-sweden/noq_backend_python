from rest_framework import serializers
from .models_volunteer_task import VolunteerTask

class VolunteerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerTask
        fields = '__all__'