from django.test import TestCase
from django.http import Http404
from parkings.tests.factories import TestParkingFactory
from parkings.selectors import (
    parking_list,
    parking_get,
    parking_get_by_name,
    check_parking_location,
)


class TestParkingSelectors(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.active_parking = TestParkingFactory.create(
            name="ActiveParking", coords=[[[0, 0], [0, 4], [4, 4], [4, 0], [0, 0]]]
        )

        cls.inactive_parking = TestParkingFactory.create(
            name="InactiveParking",
            coords=[[[5, 5], [10, 10], [0, 10], [5, 5]]],
            is_active=False,
        )

    def test_parking_list(self):
        parkings = parking_list(include_inactive=True)
        self.assertEqual(parkings.count(), 2)

    def test_parking_list_active(self):
        parkings = parking_list()
        self.assertEqual(parkings.count(), 1)
        self.assertIn(self.active_parking, parkings)

    def test_parking_get(self):
        parking = parking_get(self.inactive_parking.id)
        self.assertEqual(parking, self.inactive_parking)

    def test_parking_get_nonexistent(self):
        with self.assertRaises(Http404):
            parking_get(999)

    def test_parking_get_by_name(self):
        parking = parking_get_by_name("ActiveParking")
        self.assertEqual(parking, self.active_parking)

    def test_parking_get_by_name_nonexistent(self):
        with self.assertRaises(Http404):
            parking_get_by_name("ActiveParkin")

    def check_parking_location_valid(self):
        self.assertTrue(check_parking_location(1, 1))

    def check_parking_location_invalid(self):
        point = (5, 6)

        # Ensuring that check_parking_location only considers active parkings
        self.assertTrue(self.inactive_parking.contains_point(*point))
        self.assertFalse(check_parking_location(*point))
