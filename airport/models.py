from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Airport(models.Model):
    name = models.CharField(max_length=100)
    airport_code = models.CharField(max_length=10)
    closest_big_city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}-{self.airport_code}"

    class Meta:
        ordering = ["-name"]


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-name"]


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="routes_from")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="routes_to")
    distance = models.IntegerField()


class Order(models.Model):
    created_at = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateField()
    arrival_time = models.DateField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self):
        return self.route + " " + str(self.departure_time) + str(self.arrival_time)

    def str(self):
        departure_city = self.route.source.closest_big_city
        departure_code = self.route.source.airport_code
        arrival_city = self.route.destination.closest_big_city
        arrival_code = self.route.destination.airport_code

        departure_time = self.departure_time.strftime("%d.%m.%Y %H:%M")
        arrival_time = self.arrival_time.strftime("%d.%m.%Y %H:%M")
        return "{} ({}) - {} ({}) | {} - {}".format(
            departure_city,
            departure_code,
            arrival_city,
            arrival_code,
            departure_time,
            arrival_time
        )

    class Meta:
        verbose_name = "routes"


class Ticket(models.Model):
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    @staticmethod
    def validate_seats(
            row: int,
            seat: int,
            error_to_raise,
            flight: Flight
    ):

        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row")
        ]:
            count_attrs = getattr(
                flight.airplane, airplane_attr_name
            )
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name:
                            f"{ticket_attr_name} "
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
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
