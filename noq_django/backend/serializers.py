from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'is_registered']

    def get_is_registered(self, obj) -> bool:
        registered_ids = self.context.get('registered_ids', [])
        return obj.id in registered_ids
    

class AdminActivitySerializer(serializers.ModelSerializer):
    signed_up_volunteers = serializers.SerializerMethodField()
    test = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'is_approved', 'signed_up_volunteers', 'test']

    def get_signed_up_volunteers(self, obj):
        volunteer_activities = obj.volunteeractivity_set.all()
        return [
            {
                'id': va.volunteer.id,
                'first_name': va.volunteer.first_name,
                'last_name': va.volunteer.last_name,
                'email': va.volunteer.email,
                
            }
            for va in volunteer_activities
            ]
    def get_test(self, obj):
        return "Danilo was here"

        