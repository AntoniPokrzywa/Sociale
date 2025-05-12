from rest_framework import status
from django.urls import reverse

from utils.tests import CustomAPITestCase
from rentals.tests.factories import TestRentalFactory
from bikes.tests.factories import TestBikeFactory
from parkings.tests.factories import TestParkingFactory


class RentalApiTests(CustomAPITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.setUpAuthData()
        TestRentalFactory.create_batch(3)

        TestParkingFactory.create(
            name="boundary", coords=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]
        )

    def test_rental_list_unauth(self):
        url = reverse("rentals:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rental_list_active_user(self):
        self.authenticate(user=self.active_user)
        url = reverse("rentals:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rental_list(self):
        self.authenticate(user=self.admin)
        url = reverse("rentals:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_rental_detail_unauth(self):
        url = reverse("rentals:detail", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rental_detail(self):
        self.authenticate(user=self.admin)
        url = reverse("rentals:detail", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rental_start(self):
        self.authenticate(user=self.active_user)
        url = reverse("rentals:start")
        bike = TestBikeFactory.create(is_available=True)
        response = self.client.post(url, data={"bike": bike.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], bike.code)

    def test_rental_finish(self):
        self.authenticate(user=self.active_user)
        rental = TestRentalFactory.create(user=self.active_user, status="started")
        url = reverse("rentals:finish")
        response = self.client.post(url, data={"lon": 1, "lat": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rental.refresh_from_db()
        self.assertEqual(rental.status, "finished")

    def test_rental_update(self):
        self.authenticate(user=self.admin)
        rental = TestRentalFactory.create(status="started")
        url = reverse("rentals:update", args=[rental.id])
        response = self.client.put(url, data={"status": "finished"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rental.refresh_from_db()
        self.assertEqual(rental.status, "finished")
