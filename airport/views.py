from datetime import datetime
from django.db.models import Count, F
from rest_framework import viewsets
from airport.models import (
    Airplane,
    Crew,
    Order,
    Ticket,
    Flight,
    Airport,
    Route,
    AirplaneType
)
from airport.serializers import (
    AirplaneSerializer,
    CrewSerializer,
    AirplaneTypeSerializer,
    RouteSerializer,
    OrderSerializer,
    TicketSerializer,
    FlightSerializer,
    AirportSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    RouteListSerializer,
    AirplaneDetailSerializer,
    OrderListSerializer
)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        return AirplaneDetailSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related("route", "airplane").prefetch_related("crew")
    serializer_class = FlightSerializer

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        departure = self.request.query_params.get("departure")
        arrival = self.request.query_params.get("arrival")
        source_name = self.request.query_params.get("source_name")
        destination_name = self.request.query_params.get("destination_name")
        if departure:
            departure = datetime.strptime(departure, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure)

        if arrival:
            arrival = datetime.strptime(arrival, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival)

        if source_name:
            source_ids = self._params_to_ints(source_name)
            queryset = queryset.filter(route__source_id__in=source_ids)

        if destination_name:
            destination_ids = self._params_to_ints(destination_name)
            queryset = queryset.filter(route__destination_id__in=destination_ids)

        if self.action == "list":
            queryset = (
                queryset.select_related(
                    "route",
                    "airplane"
                ).prefetch_related(
                    "route__source",
                    "route__destination",
                    "crew"
                )
            ).annotate(
                    tickets_available=(
                            F("airplane__rows")
                            * F("airplane__seats_in_row")
                            - Count("tickets")

                    )
                ).order_by("id")
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related("flight", "order")
    serializer_class = TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related("user")
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == ["list", "detail"]:
            queryset = queryset.prefetch_related(
                "tickets__flight__airplane"
            )


        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteSerializer

        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
