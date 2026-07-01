"""Admin Django. User utilise l'admin par défaut ; on expose le journal RGPD."""

from django.contrib import admin

from .models import DataRequest


@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    """Audit trail des demandes RGPD (SAR) — lecture seule."""

    list_display = ("created_at", "request_type", "export_format", "user_email", "ip_address")
    list_filter = ("request_type", "export_format", "created_at")
    search_fields = ("user_email",)
    readonly_fields = (
        "user",
        "user_email",
        "request_type",
        "export_format",
        "ip_address",
        "created_at",
    )

    def has_add_permission(self, request):
        return False  # les demandes ne se créent que via l'API
