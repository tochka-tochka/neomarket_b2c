import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from neomarket_b2c import settings


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="jwt_user", password="password123")


@pytest.fixture
def jwt_client(api_client, test_user):
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.defaults
    return api_client


@pytest.fixture(autouse=True)
def mock_service_key(monkeypatch):
    monkeypatch.setenv('MODER_SERVICE_KEY', 'test_key_123')
    monkeypatch.setenv('B2B_SERVICE_KEY', 'test_key_123')


@pytest.fixture
def service_client(client):
    client.defaults['HTTP_X_SERVICE_KEY'] = 'test_key_123'
    return client


@pytest.fixture(scope="session", autouse=True)
def force_close_connections(django_db_setup, django_db_blocker):
    yield
    with django_db_blocker.unblock():
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = current_database()
                  AND pid <> pg_backend_pid();
            """)