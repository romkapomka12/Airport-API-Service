# Generated by Django 5.0 on 2023-12-06 12:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("airport", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="destination",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routes_to",
                to="airport.airport",
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routes_from",
                to="airport.airport",
            ),
        ),
        migrations.AddField(
            model_name="flight",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="airport.route"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="flight",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="airport.flight",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="airport.order",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("flight", "row", "seat")},
        ),
    ]
