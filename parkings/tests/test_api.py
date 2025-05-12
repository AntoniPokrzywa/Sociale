import json
from django.urls import reverse
from rest_framework import status

from parkings.models import Parking
from parkings.tests.factories import TestParkingFactory
from utils.tests import CustomAPITestCase


class ParkingApiTests(CustomAPITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.setUpAuthData()

        cls.parking_data = {
            "name": "Parking",
            "capacity": 12,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [19.896595, 50.008492],
                        [19.897456, 50.009673],
                        [19.895648, 50.009341],
                        [19.896595, 50.008492],
                    ]
                ],
            },
        }
        TestParkingFactory.create(
            name="boundary",
            coords=[
                [19.867737, 49.999826],
                [19.831094, 50.013598],
                [19.906522, 50.034662],
                [19.931808, 49.981917],
                [19.867737, 49.999826],
            ],
        )
        cls.parking = TestParkingFactory.create(
            name="TempParking",
            coords=[
                [19.896595, 50.008492],
                [19.897456, 50.009673],
                [19.895648, 50.009341],
                [19.896595, 50.008492],
            ],
        )
        cls.inactive_parking = TestParkingFactory.create(
            name="InactiveParking",
            coords=[
                [19.894835, 50.009293],
                [19.895590, 50.010333],
                [19.897441, 50.009824],
                [19.894835, 50.009293],
            ],
            is_active=False,
        )

    def parking_create(self, data):
        url = reverse("parkings:create")
        return self.client.post(url, data=data, format="json")

    def test_parking_list_noauth(self):
        url = reverse("parkings:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_list_by_active_user(self):
        url = reverse("parkings:list")
        self.authenticate(self.active_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(f"{url}?include_inactive=True")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_list_including_inactive(self):
        url = reverse("parkings:list")
        self.authenticate(self.admin)
        response = self.client.get(f"{url}?include_inactive=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_parking_get(self):
        url = reverse("parkings:detail", args=[self.parking.id])
        self.authenticate(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("geometry"), json.loads(self.parking.area))

    def test_parking_get_nonexistent(self):
        url = reverse("parkings:detail", args=[000])
        self.authenticate(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_parking_create_noauth(self):
        response = self.parking_create(self.parking_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_create_by_user(self):
        # Active Users should't be able to create new parkings
        self.authenticate(self.active_user)
        response = self.parking_create(self.parking_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_create_by_admin(self):
        self.authenticate(self.admin)
        response = self.parking_create(self.parking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_parking_create_duplicate_name(self):
        self.authenticate(self.admin)
        self.parking_create(self.parking_data)

        response = self.parking_create(self.parking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parking_create_invalid_area(self):
        self.authenticate(self.admin)
        invalid_data = {
            "name": "Invalid Parking",
            "capacity": 10,
            "geometry": {  # Incorrect format coords (not nested list)
                "type": "Polygon",
                "coordinates": [
                    [19.896595, 50.008492],
                    [19.897456, 50.009673],
                    [19.895648, 50.009341],
                    [19.896595, 50.008492],
                ],
            },
        }
        response = self.parking_create(invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid GeoJSON data provided", str(response.data))

    def test_parking_create_negative_capacity(self):
        self.authenticate(self.admin)
        invalid_data = {
            "name": "Negative Parking",
            "capacity": -12,
            "area": self.parking_data["geometry"],
        }

        response = self.parking_create(invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parking_update(self):
        self.authenticate(self.admin)
        url = reverse("parkings:update", args=[self.parking.id])

        update_data = {
            "name": "UpdatedParking",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [19.898263, 50.010333],
                        [19.895659, 50.010537],
                        [19.896729, 50.011653],
                        [19.898263, 50.010333],
                    ]
                ],
            },
        }
        response = self.client.put(url, data=update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.parking.refresh_from_db()
        self.assertEqual(self.parking.name, update_data["name"])
        self.assertEqual(self.parking.area, json.dumps(update_data["geometry"]))

    def test_parking_update_outside_boundaries(self):
        self.authenticate(self.admin)
        url = reverse("parkings:update", args=[self.parking.id])

        invalid_update_data = {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [19.825235, 49.999686],
                        [19.791530, 49.990296],
                        [19.802390, 49.966935],
                        [19.825235, 49.999686],
                    ]
                ],
            }
        }
        response = self.client.put(url, data=invalid_update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parking_delete(self):
        self.authenticate(self.admin)
        url = reverse("parkings:delete", args=[self.parking.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Parking.objects.filter(id=self.parking.id).exists())

    def test_parking_delete_nonexistent(self):
        self.authenticate(self.admin)
        url = reverse("parkings:delete", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
