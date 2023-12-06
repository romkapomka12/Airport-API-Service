from django.contrib import admin

from airport.models import (Flight,
                            Crew,
                            Airport,
                            AirplaneType,
                            Route,
                            Order,
                            Ticket)

admin.site.register(Flight)
admin.site.register(Crew)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Ticket)
