import os
import tempfile
from PIL import Image
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneSerializer

AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="Large Jets")

    defaults = {
        "name": "Boeing 777X",
        "rows": 250,
        "seats_in_row": 2,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Large Jets",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def detail_url(airplane_id: int):
    return reverse("airport:airplane-detail", args=[airplane_id])


def image_upload_url(airplane_id):
    """Return URL for recipe image upload"""

    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticateAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )
        self.client.force_authenticate(self.user)

        self.airplane_type = AirplaneType.objects.create(name="Large Jets")
        self.airplane = Airplane.objects.create(
            name="Boeing 777X",
            rows=250,
            seats_in_row=2,
            airplane_type=self.airplane_type,
        )

    def test_list_airplane(self):
        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_flight_detail(self):
        pass

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Boeing 777X",
            "rows": 250,
            "seats_in_row": 2,
            "airplane_type": self.airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazxcde3", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)
        self.airplane_type = AirplaneType.objects.create(name="Large Jets")
        self.defaults = {
            "name": "Boeing 777X",
            "rows": 250,
            "seats_in_row": 2,
            "airplane_type": self.airplane_type,
        }

    def test_list_airplane(self):
        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(name="Large Jets")

        payload = {
            "name": "Boeing 777X",
            "rows": 250,
            "seats_in_row": 2,
            "airplane_type": airplane_type.id,
        }

        response = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(airplane.airplane_type, airplane_type)

    def test_delete_airplane_not_allowed(self):
        airplane = Airplane.objects.create(
            name="Boeing 777X",
            rows=250,
            seats_in_row=2,
            airplane_type=self.airplane_type,
        )
        url = detail_url(airplane.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()
        self.name = sample_airplane()
        self.rows = sample_airplane()
        self.seats_in_row = sample_airplane()
        self.airplane_type = sample_airplane_type()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to airplane"""

        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list(self):
        AIRPLANE_URL_IMAGE = reverse(
            "airport:airplane-upload-image", args=[self.airplane.id]
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                AIRPLANE_URL_IMAGE, {"image": ntf}, format="multipart"
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            airplane = Airplane.objects.get(id=self.airplane.id)
            self.assertTrue(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        airplane = sample_airplane()
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                reverse("airport:airplane-upload-image", args=[airplane.id]),
                {"image": ntf},
                format="multipart",
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            res = self.client.get(
                reverse("airport:airplane-detail", args=[airplane.id])
            )
            self.assertIn("image_url", res.data)
            self.assertNotEqual(res.data["image_url"], "")
