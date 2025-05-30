from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client as TestClient
from backend.models import Client, UserProfile, Region
import base64
import json

class TestUserProfileAPI(TestCase):
    def auth_headers(self, username=None, password=None):
        user = username or self.username
        pwd = password or self.password
        credentials = f"{user}:{pwd}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"HTTP_AUTHORIZATION": f"Basic {encoded}"}

    def setUp(self):
        self.username = "testuser@example.com"
        self.password = "securepass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        self.region = Region.objects.create(name="Test Region")
        self.client_obj = Client.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            unokod="12345",
            gender="M",
            region=self.region
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            client=self.client_obj,
            language="en",
            presentation="Hello, I am John"
        )
        self.client = TestClient()
        self.client.login(username=self.username, password=self.password)

    def test_list_profiles(self):
        response = self.client.get("/api/preferences/", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        # Check all required fields exist
        for key in ["id", "user_id", "uno", "first_name", "last_name", "email"]:
            self.assertIn(key, data[0])

    def test_get_profile(self):
        response = self.client.get(f"/api/preferences/{self.user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.profile.id)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["uno"], self.client_obj.unokod)
        # Optional fields
        self.assertEqual(data.get("language"), "en")
        self.assertEqual(data.get("presentation"), "Hello, I am John")

    def test_get_profile_unauthorized(self):
        # Another user
        other_user = User.objects.create_user(username="other@example.com", password="pass123")
        response = self.client.get(f"/api/preferences/{other_user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 403)

    def test_create_profile(self):
        # Create a new user
        username = "jane@example.com"
        password = "securepass123"
        new_user = User.objects.create_user(
            username=username,
            password=password,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        region = Region.objects.create(name="Region Two")
        new_client = Client.objects.create(
            user=new_user,
            first_name="Jane",
            last_name="Smith",
            unokod="54321",
            gender="F",
            region=region
        )
        # Log in as the new user
        self.client.logout()
        self.client.login(username=username, password=password)
        payload = {
            "language": "sv",
            "presentation": "Hej, jag är Jane",
            "supporting_person_id": None
        }
        # If your POST expects JSON, use content_type
        response = self.client.post("/api/preferences/", data=json.dumps(payload),
                                    content_type="application/json", **self.auth_headers(username, password))
        self.assertIn(response.status_code, (200, 201))
        data = response.json()
        self.assertEqual(data["first_name"], "Jane")
        self.assertEqual(data["last_name"], "Smith")
        self.assertEqual(data["uno"], "54321")

    def test_create_profile_duplicate_uno(self):
        # Try to create a new profile with same uno
        username = "dup@example.com"
        password = "securepass123"
        new_user = User.objects.create_user(
            username=username,
            password=password,
            first_name="Dup",
            last_name="Smith",
            email="dup.smith@example.com"
        )
        region = Region.objects.create(name="Region Dup")
        _ = Client.objects.create(
            user=new_user,
            first_name="Dup",
            last_name="Smith",
            unokod="12345",  # Same as self.client_obj.unokod!
            gender="M",
            region=region
        )
        self.client.logout()
        self.client.login(username=username, password=password)
        payload = {
            "language": "en",
            "presentation": "Trying duplicate uno",
            "supporting_person_id": None
        }
        response = self.client.post("/api/preferences/", data=json.dumps(payload),
                                    content_type="application/json", **self.auth_headers(username, password))
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json().get("detail", ""))

    def test_update_profile(self):
        payload = {
            "language": "fr",
            "presentation": "Bonjour!",
            "supporting_person_id": None
        }
        response = self.client.patch(
            f"/api/preferences/{self.user.id}",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["language"], "fr")
        self.assertEqual(data["presentation"], "Bonjour!")

    def test_update_profile_unauthorized(self):
        other_user = User.objects.create_user(username="unauth@example.com", password="pass123")
        payload = {"presentation": "Should fail"}
        response = self.client.patch(
            f"/api/preferences/{other_user.id}",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_profile(self):
        response = self.client.delete(f"/api/preferences/{self.user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("success"), True)
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())

    def test_delete_profile_unauthorized(self):
        other_user = User.objects.create_user(username="other2@example.com", password="pass123")
        region = Region.objects.create(name="Region del2")
        other_client = Client.objects.create(
            user=other_user,
            first_name="Other",
            last_name="Two",
            unokod="77777",
            gender="F",
            region=region
        )
        other_profile = UserProfile.objects.create(user=other_user, client=other_client)
        response = self.client.delete(f"/api/preferences/{other_user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        UserProfile.objects.all().delete()
        Client.objects.all().delete()
        User.objects.all().delete()
        Region.objects.all().delete()