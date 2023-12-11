from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Airplane,
    Flight,
    Ticket,
    Order,
    Route,
    AirplaneType,
    Crew,
    Airport
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "airport_code", "closest_big_city")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(many=False)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField(many=False)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = RouteSerializer(many=False, read_only=True)
    destination = RouteSerializer(many=False, read_only=True)


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField(many=False)
    destination = serializers.StringRelatedField(many=False)


class TicketSerializer(serializers.ModelSerializer):

    def validate(self, attrs) -> dict:
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seats(
            attrs["row"],
            attrs["seat"],
            serializers.ValidationError,
            attrs["flight"],
        )
        return data

    class Meta:
        model = Ticket
        fields = ("flight", "row", "seat")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightDetailSerializer(FlightSerializer):
    # route = serializers.StringRelatedField(many=False)
    # airplane = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")

    route = RouteSerializer(
        many=False,
        read_only=True
    )
    airplane = AirplaneSerializer(
        many=False,
        read_only=True
    )
    taken_places = TicketSeatsSerializer(
        many=True,
        read_only=True,
        source="tickets"
    )

    class Meta:
        model = Flight

        fields = ("id", "departure_time", "arrival_time", "route", "airplane", "taken_places")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False)
    airplane = serializers.StringRelatedField(many=False)
    airplane_num_seats = serializers.IntegerField(source="airplane.capacity", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "airplane_num_seats", "tickets_available")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=False)
