from django.contrib import admin
from .forms import FlightForm
from airport.models import (Flight,
                            Crew,
                            Airport,
                            AirplaneType,
                            Route,
                            Order,
                            Ticket,
                            Airplane)


class FlightAdmin(admin.ModelAdmin):
    form = FlightForm


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)


admin.site.register(Flight, FlightAdmin)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Route)

admin.site.register(Ticket)
