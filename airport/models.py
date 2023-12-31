import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{extension}"
    return os.path.join("uploads/airplanes//", filename)


class Crew(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if (
                Crew.objects.exclude(pk=self.pk)
                        .filter(first_name=self.first_name, last_name=self.last_name)
                        .exists()
        ):
            raise ValidationError("Crew with this full name already exists.")
        super().save(*args, **kwargs)


class Airport(models.Model):
    name = models.CharField(max_length=100)
    airport_code = models.CharField(max_length=10, unique=True)
    closest_big_city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name},{self.closest_big_city}({self.airport_code})"

    class Meta:
        ordering = ["name"]


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-name"]


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_to"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}"

    class Meta:
        ordering = ["source"]

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "The city of departure and arrival cannot be the same"
            )


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        indexes = [models.Index(fields=["departure_time", "arrival_time"])]

    def __str__(self):
        departure_time = self.departure_time.strftime("%Y-%m-%d  %H:%M")
        arrival_time = self.arrival_time.strftime("%Y-%m-%d  %H:%M")
        return str(
            f"{self.route.source.closest_big_city} ({self.route.source.airport_code}) - "
            f" {self.route.destination.closest_big_city} ({self.route.destination.airport_code}) | "
            f"Departure Time - {departure_time} | "
            f"Return Time - {arrival_time}"
        )

    @property
    def tickets_available(self):
        return self.airplane.rows * self.airplane.seats_in_row - self.tickets.count()


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
    row = models.IntegerField()
    seat = models.IntegerField()

    @staticmethod
    def validate_seats(row: int, seat: int, error_to_raise, flight: Flight):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(flight.airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        Ticket.validate_seats(
            self.row,
            self.seat,
            ValidationError,
            self.flight,
        )

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super(Ticket, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row"]
