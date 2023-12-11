from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from airport.models import Flight


def validate_crew(value):
    if value != 2:
        raise ValidationError(
            _("%(value)s is not a valid crew size"),
            params={"value": value},
        )


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ["route", "airplane", "departure_time", "arrival_time", "crew"]

    def clean_crew(self):
        crew = self.cleaned_data.get("crew")
        validate_crew(crew.count())
        return crew
