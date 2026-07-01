"""Fixtures partagées pour les tests adversariaux J3."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def auth_client() -> APIClient:
    user = User.objects.create_user(username="adversarial", password="motdepasse123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client
