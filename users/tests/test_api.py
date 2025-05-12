import re
from django.urls import reverse
from django.core import mail
from rest_framework import status
from users.models import User
from users.tests.factories import TestUserFactory
from utils.tests import CustomAPITestCase


class UserApiTests(CustomAPITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.setUpAuthData()

    def login(self, email, password):
        url = reverse("users:login")
        return self.client.post(url, {"email": email, "password": password})

    def test_user_login(self):
        response = self.login("chillguy@sociale.com", "ilovesociale")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_brute_force(self):
        for _ in range(5):
            response = self.login("randomguy@random.com", "wrongpass")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.login("randomguy@random.com", "wrongpass")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_list_admin(self):
        self.authenticate(self.admin)
        url = reverse("users:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_list_user(self):
        self.authenticate(self.active_user)
        url = reverse("users:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail(self):
        self.authenticate(self.admin)
        url = reverse("users:detail", args=[self.active_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_nonexistent(self):
        self.authenticate(self.admin)
        url = reverse("users:detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_register(self):
        url = reverse("users:register")
        data = {
            "email": "validname@sociale.com",
            "first_name": "Chill",
            "last_name": "Guy",
            "password": "StrongPass123",
            "confirmed_password": "StrongPass123",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=data["email"])
        self.assertFalse(user.is_verified)
        self.assertEqual(mail.outbox[0].subject, "Verify your account")

        verification_link = (
            re.search(r"http[s]?://\S+", mail.outbox[0].body).group().split("/")
        )
        token = verification_link[-1]
        uid = verification_link[-2]

        url = reverse("users:verify-email")
        response = self.client.post(url, data={"uid": uid, "token": token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verify_email_invalid_data(self):
        url = reverse("users:verify-email")
        response = self.client.post(url, data={"uid": "invalid", "token": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_existing_email(self):
        url = reverse("users:register")
        data = {
            "email": "chillguy@sociale.com",
            "first_name": "Chill",
            "last_name": "Guy",
            "password": "pass",
            "confirmed_password": "pass",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email already exists", str(response.data))

    def test_register_password_mismatch(self):
        url = reverse("users:register")
        data = {
            "email": "newuser@sociale.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "confirmed_password": "password456",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update(self):
        self.authenticate(self.admin)
        user = TestUserFactory.create(is_active=False)
        url = reverse("users:update", args=[user.id])
        response = self.client.put(url, {"is_active": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(id=user.id).is_active)

    def test_admin_can_delete_user(self):
        self.authenticate(self.admin)
        user = TestUserFactory.create()
        url = reverse("users:delete", args=[user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user.id).exists())

    def test_user_can_delete_user(self):
        self.authenticate(self.active_user)
        url = reverse("users:delete", args=[self.verified_not_active_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_reset(self):
        url = reverse("users:reset-password-request")
        response = self.client.post(url, {"email": self.active_user.email})
        self.assertEqual(mail.outbox[0].subject, "Reset your password")
        verification_link = (
            re.search(r"http[s]?://\S+", mail.outbox[0].body).group().split("/")
        )

        token = verification_link[-1]
        uid = verification_link[-2]
        url = reverse("users:reset-password-check")

        password = "pass123"
        response = self.client.put(
            url,
            {
                "uid": uid,
                "token": token,
                "password": password,
                "confirmed_password": password,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password(password))

    def test_password_reset_invalid_email(self):
        url = reverse("users:reset-password-request")
        response = self.client.post(url, {"email": "idontexist@sociale.com"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(mail.outbox), 0)
