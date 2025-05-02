from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.test import Client as TestClient
from backend.models import Resource
from datetime import time
import json
import base64


class TestVolunteerCompassAPI(TestCase):
    def auth_headers(self):
      credentials = f"{self.username}:{self.password}"
      encoded = base64.b64encode(credentials.encode()).decode()
      return {"HTTP_AUTHORIZATION": f"Basic {encoded}"}

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
            target_group="Över 18",
            other="Test Note",
            applies_to=["Psykisk ohälsa", "Missbruk"]
        )

    def test_list_resources(self):
        # response = self.client.get("/api/volunteer/compass/")
        response = self.client.get("/api/volunteer/compass/", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_get_resource_by_id(self):
        response = self.client.get(f"/api/volunteer/compass/resources/{self.resource.id}", **self.auth_headers())
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
            "target_group": "Under 18",
            "other": "Created via test",
            "applies_to": ["Sysselsättning", "Studier"]
        }
        response = self.client.post(
            "/api/volunteer/compass/",
            data=json.dumps(new_data),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "Created Resource")

    def test_patch_resource(self):
        response = self.client.patch(
            f"/api/volunteer/compass/resources/{self.resource.id}",
            data=json.dumps({"phone": "0000000000"}),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.phone, "0000000000")

    def test_delete_resource(self):
        response = self.client.delete(f"/api/volunteer/compass/resources/{self.resource.id}", **self.auth_headers())
        #response = self.client.delete(f"/api/volunteer/compass/resources/{self.resource.id}")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Resource.objects.filter(id=self.resource.id).exists())

    def test_filter_by_target_group(self):
        Resource.objects.create(
            name="Youth Center",
            opening_time=time(8, 0),
            closing_time=time(16, 0),
            address="Somewhere",
            phone="123",
            email="youth@example.com",
            target_group="Under 18",
            other="Youth programs",
            applies_to=["Sysselsättning"]
        )
        response = self.client.get("/api/volunteer/compass/?target_group=Under 18", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Youth Center" in r["name"] for r in response.json()))

    def test_filter_by_applies_to(self):
        Resource.objects.create(
            name="Crisis Support",
            opening_time=time(10, 0),
            closing_time=time(18, 0),
            address="Anywhere",
            phone="456",
            email="crisis@example.com",
            target_group="Alla åldrar",
            other="Help for crisis",
            applies_to=["Psykisk ohälsa"]
        )
        response = self.client.get("/api/volunteer/compass/?applies_to=Psykisk ohälsa", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Crisis Support" in r["name"] for r in response.json()))

    def test_search_by_keyword(self):
        Resource.objects.create(
            name="Göteborg Center",
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            address="Göteborg",
            phone="789",
            email="goteborg@example.com",
            target_group="Alla åldrar",
            other="Local help",
            applies_to=["Missbruk"]
        )
        response = self.client.get("/api/volunteer/compass/?search=goteborg", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Göteborg Center" in r["name"] for r in response.json()))

    def test_sort_by_name_az(self):
        Resource.objects.create(
            name="Alpha Resource",
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            address="Alpha St",
            phone="111",
            email="alpha@example.com",
            target_group="Alla åldrar",
            other="Alpha description",
            applies_to=["Missbruk"]
        )
        Resource.objects.create(
            name="Beta Resource",
            opening_time=time(10, 0),
            closing_time=time(18, 0),
            address="Beta St",
            phone="222",
            email="beta@example.com",
            target_group="Alla åldrar",
            other="Beta description",
            applies_to=["Sysselsättning"]
        )
        response = self.client.get("/api/volunteer/compass/?sort=name", **self.auth_headers())
        names = [r["name"] for r in response.json() if r["name"] in ["Alpha Resource", "Beta Resource"]]
        self.assertEqual(names, sorted(names))