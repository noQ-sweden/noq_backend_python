from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client as TestClient
from datetime import datetime, date
import json
import base64

from backend.models import UserProfile


class TestUserProfileAPI(TestCase):
    def auth_headers(self):
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"HTTP_AUTHORIZATION": f"Basic {encoded}"}

    def setUp(self):
        # Setup test user
        self.username = "testuser@example.com"
        self.password = "securepass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = TestClient()
        self.client.login(username=self.username, password=self.password)

        # Create a test profile
        self.user_profile = UserProfile.objects.create(
            user=self.user,         
            uno="12345",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            sex="M",
            birthday=date(1990, 1, 1),
            birth_year=1990,
            language="en",
            presentation="Hello, I am John"
        )

    def test_list_profiles(self):
        """Test getting all profiles"""
        response = self.client.get("/api/preferences/", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "John")

    def test_get_profile(self):
        """Test getting a specific profile"""
        response = self.client.get(f"/api/preferences/{self.user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["email"], "john.doe@example.com")

    def test_get_profile_unauthorized(self):
        """Test getting another user's profile (should fail)"""
        other_user = User.objects.create_user(username="other@example.com", password="pass123")
        response = self.client.get(f"/api/preferences/{other_user.id}", **self.auth_headers())
        self.assertEqual(response.status_code, 403)

    def test_create_profile(self):
        """Test creating a new profile"""
        # Delete existing profile for this test
        self.user_profile.delete()
        
        new_data = {
            "uno": "54321",
            "first_name": "Jane",
            "last_name": "Smith",
            "sex": "F",
            "birthday": "1992-02-02",
            "birth_year": 1992,
            "email": "jane.smith@example.com",
            "telephone": "123456789",
            "language": "en",
            "presentation": "Hello, I am Jane",
            "supporting_person_id": None
        }
        response = self.client.post(
            "/api/preferences/",
            data=json.dumps(new_data),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Jane")
        self.assertEqual(data["uno"], "54321")

    def test_create_profile_duplicate_uno(self):
        """Test creating a profile with duplicate UNO (should fail)"""
        new_data = {
            "uno": "12345",  # Same UNO as existing profile
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "language": "en"
        }
        response = self.client.post(
            "/api/preferences/",
            data=json.dumps(new_data),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("UNO already exists", response.json()["detail"])

    def test_update_profile(self):
        """Test updating a profile"""
        update_data = {
            "first_name": "Johnny",
            "last_name": "Updated",
            "email": "johnny.updated@example.com"
        }
        response = self.client.patch(
            f"/api/preferences/{self.user.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Johnny")
        self.assertEqual(data["last_name"], "Updated")
        self.assertEqual(data["email"], "johnny.updated@example.com")

    def test_delete_profile(self):
        """Test deleting a profile"""
        response = self.client.delete(
            f"/api/preferences/{self.user.id}",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 0)

    def test_delete_profile_unauthorized(self):
        """Test deleting another user's profile (should fail)"""
        other_user = User.objects.create_user(username="other@example.com", password="pass123")
        response = self.client.delete(
            f"/api/preferences/{other_user.id}",
            **self.auth_headers()
        )
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        User.objects.all().delete()
        UserProfile.objects.all().delete()
