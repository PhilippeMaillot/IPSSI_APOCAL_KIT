"""Ajoute DataRequest : audit trail des demandes RGPD (SAR) — perturbation J3-bis."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user_email",
                    models.EmailField(
                        blank=True,
                        help_text="Snapshot de l'email au moment de la demande (conservé même après suppression).",
                        max_length=254,
                    ),
                ),
                (
                    "request_type",
                    models.CharField(
                        choices=[("export", "Export des données (accès / portabilité)")],
                        default="export",
                        max_length=20,
                    ),
                ),
                ("export_format", models.CharField(default="json", help_text="json ou csv", max_length=8)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="data_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Demande RGPD (SAR)",
                "verbose_name_plural": "Demandes RGPD (SAR)",
                "ordering": ["-created_at"],
            },
        ),
    ]
