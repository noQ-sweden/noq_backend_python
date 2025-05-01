from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.test import Client as TestClient
from backend.models import Resource
from datetime import time
import json

class TestVolunteerCompassAPI(TestCase):
    def setUp(self):
        self.username = "volunteer@test.com"
        self.password = "securepass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

        volunteer_group, _ = Group.objects.get_or_create(name="volunteer")
        self.user.groups.add(volunteer_group)

        self.client = TestClient()
        self.client.login(username=self.username, password=self.password)

        self.resource = Resource.objects.create(
            name="Test Center",
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            address="123 Main St",
            phone="1234567890",
            email="test@example.com",
            target_group="Adults",
            other="Test Note",
            applies_to=["EU Citizens"]
        )

    def test_list_resources(self):
        response = self.client.get("/api/volunteer/compass/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_get_resource_by_id(self):
        response = self.client.get(f"/api/volunteer/compass/resources/{self.resource.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.resource.id)

    def test_create_resource(self):
        new_data = {
            "name": "Created Resource",
            "opening_time": "08:00:00",
            "closing_time": "16:00:00",
            "address": "New St",
            "phone": "9876543210",
            "email": "new@example.com",
            "target_group": "Students",
            "other": "Created via test",
            "applies_to": ["Non-EU Citizens"]
        }
        response = self.client.post(
            "/api/volunteer/compass/",
            data=json.dumps(new_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

    def test_patch_resource(self):
        response = self.client.patch(
            f"/api/volunteer/compass/resources/{self.resource.id}",
            data=json.dumps({"phone": "0000000000"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.phone, "0000000000")

    def test_delete_resource(self):
        response = self.client.delete(f"/api/volunteer/compass/resources/{self.resource.id}")
        self.assertEqual(response.status_code, 204)