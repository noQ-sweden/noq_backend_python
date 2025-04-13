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
