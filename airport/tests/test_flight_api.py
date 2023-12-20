import datetime
from datetime import datetime
import pytz
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from airport.models import Flight, Route, Airplane, AirplaneType, Crew, Airport
from airport.serializers import FlightListSerializer, FlightDetailSerializer

FLIGHT_URL = reverse("airport:flight-list")

def detail_url(flight_id: int):
    return reverse("airport:flight-detail", args=[flight_id])


def sample_flight1(**params):
    Airport1 = Airport.objects.create(
        name="Geneva", airport_code="GTR", closest_big_city="Geneva"
    )
    Airport2 = Airport.objects.create(
        name="Washington", airport_code="RTY", closest_big_city="Washington"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=1900)
    airplane_type = AirplaneType.objects.create(name="Large Jets")
    airplane = Airplane.objects.create(
        name="Boeing 777X", rows=250, seats_in_row=2, airplane_type=airplane_type
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2023-12-15 13:07:09",
        "arrival_time": "2023-12-15 16:00:00",
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def sample_flight2(**params):
    Airport1 = Airport.objects.create(
        name="Bucharest", airport_code="OTP", closest_big_city="Bucharest"
    )
    Airport2 = Airport.objects.create(
        name="Boryspil", airport_code="KVB", closest_big_city="Boryspil"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=900)
    airplane_type = AirplaneType.objects.create(name="Planes of local airline(16 C)")
    airplane = Airplane.objects.create(
        name="Airbus A380", rows=150, seats_in_row=2, airplane_type=airplane_type
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2023-12-14 10:07:09",
        "arrival_time": "2023-12-14 16:00:00",
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def sample_flight3(**params):
    Airport1 = Airport.objects.create(
        name="Aberdeen", airport_code="ABZ", closest_big_city="Aberdeen"
    )
    Airport2 = Airport.objects.create(
        name="Valencia", airport_code="VLC", closest_big_city="Valencia"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=500)
    airplane_type = AirplaneType.objects.create(name="Medium Jets")
    airplane = Airplane.objects.create(
        name="McDonnell Douglas DC-10",
        rows=180,
        seats_in_row=2,
        airplane_type=airplane_type,
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2023-12-17 10:07:09",
        "arrival_time": "2023-12-17 16:00:00",
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_flight(self):
        sample_flight1()
        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_departure(self):
        flight1 = sample_flight1()
        flight2 = sample_flight2()
        flight3 = sample_flight3()

        res = self.client.get(FLIGHT_URL, {"departure": "2023-12-17"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)
        serializer3 = FlightListSerializer(flight3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_filter_flight_by_arrival(self):
        flight1 = sample_flight1()
        flight2 = sample_flight2()
        flight3 = sample_flight3()

        res = self.client.get(FLIGHT_URL, {"arrival": "2023-12-17"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)
        serializer3 = FlightListSerializer(flight3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_retrieve_flight_detail(self):
        flight1 = sample_flight1()

        url = detail_url(flight1.id)
        response = self.client.get(url)

        serializer = FlightDetailSerializer(flight1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airplane_forbidden(self):
        Airport1 = Airport.objects.create(
            name="Aberdeen", airport_code="ABZ", closest_big_city="Aberdeen"
        )
        Airport2 = Airport.objects.create(
            name="Valencia", airport_code="VLC", closest_big_city="Valencia"
        )
        route = Route.objects.create(
            source=Airport1, destination=Airport2, distance=500
        )
        airplane_type = AirplaneType.objects.create(name="Medium Jets")
        airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=180,
            seats_in_row=2,
            airplane_type=airplane_type,
        )
        payload = {
            "route": route.pk,
            "airplane": airplane.pk,
            "departure_time": "2023-12-17 10:07:09",
            "arrival_time": "2023-12-17 16:00:00",
        }

        response = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazxcde3", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_flight(self):
        Airport1 = Airport.objects.create(
            name="Aberdeen", airport_code="ABZ", closest_big_city="Aberdeen"
        )
        Airport2 = Airport.objects.create(
            name="Valencia", airport_code="VLC", closest_big_city="Valencia"
        )
        route = Route.objects.create(
            source=Airport1, destination=Airport2, distance=500
        )
        airplane_type = AirplaneType.objects.create(name="Medium Jets")
        airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=180,
            seats_in_row=2,
            airplane_type=airplane_type,
        )
        crew_1 = Crew.objects.create(first_name="Crew1", last_name="Member1")
        crew_2 = Crew.objects.create(first_name="Crew2", last_name="Member2")
        payload = {
            "route": route.pk,
            "airplane": airplane.pk,
            "departure_time": "2023-12-17 10:07:09",
            "arrival_time": "2023-12-17 16:00:00",
            "crew": [crew_1.pk, crew_2.pk],
        }
        response = self.client.post(FLIGHT_URL, payload)
        Flight.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key, value in payload.items():
            if key in ("departure_time", "arrival_time"):
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                tz = pytz.timezone("Europe/Kiev")
                value = tz.localize(value)
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            self.assertEqual(response.data[key], value)

    def test_create_flight_with_two_crew_members(self):
        Airport1 = Airport.objects.create(
            name="Aberdeen", airport_code="ABZ", closest_big_city="Aberdeen"
        )
        Airport2 = Airport.objects.create(
            name="Valencia", airport_code="VLC", closest_big_city="Valencia"
        )
        route = Route.objects.create(
            source=Airport1, destination=Airport2, distance=500
        )
        airplane_type = AirplaneType.objects.create(name="Medium Jets")
        airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=180,
            seats_in_row=2,
            airplane_type=airplane_type,
        )
        crew_1 = Crew.objects.create(first_name="Crew1", last_name="Member1")
        crew_2 = Crew.objects.create(first_name="Crew2", last_name="Member2")

        payload = {
            "route": route.pk,
            "airplane": airplane.pk,
            "departure_time": "2023-12-17 10:07:09",
            "arrival_time": "2023-12-17 16:00:00",
            "crew": [crew_1.pk, crew_2.pk],
        }

        response = self.client.post(FLIGHT_URL, payload)
        flight1 = Flight.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(flight1.crew.count(), 2)

    def test_delete_light_not_allowed(self):

        flight1 = sample_flight1()
        url = detail_url(flight1.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
