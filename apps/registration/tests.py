import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from organizations.models import Organization
from django.contrib.auth.models import Group
from mini_jira import constants


@pytest.fixture
def api_client():
    """Fixture to create a reusable API client."""
    return APIClient()


@pytest.fixture
def organization():
    return Organization.objects.create(
        name="default_org",
    )

@pytest.fixture
def admin_user_group():
    return Group.objects.create(
        name=constants.ADMIN,
    )


@pytest.fixture
def member_user_group():
    return Group.objects.create(
        name=constants.MEMBER,
    )


@pytest.fixture
def valid_organization_data():
    """Fixture to create valid organization data."""
    return {
        "name": "My Organization",
    }


@pytest.fixture
def valid_user_data(organization):
    """Fixture to create valid user data."""
    return {
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "user_group": "Admin",
        "email": "johndoe@example.com",
        "password": "password123",
        "organization_id": organization.id
    }


@pytest.fixture
def invalid_user_data():
    """Fixture to create invalid user data."""
    return {
        "username": "johndoe",
        "email": "not-an-email",
        "password": "password123"
    }


@pytest.fixture
def valid_organization(valid_organization_data):
    """Fixture to create a valid organization in the database."""
    return Organization.objects.create(**valid_organization_data)


# Test Case 1: Register Organization
@pytest.mark.django_db
def test_register_organization(api_client, valid_organization_data):
    url = reverse("register_org")
    response = api_client.post(url, valid_organization_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == valid_organization_data["name"]


# Test Case 2: Register User
@pytest.mark.django_db
def test_register_user(api_client, valid_user_data, ):
    url = reverse("register_user")
    response = api_client.post(url, valid_user_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == valid_user_data["username"]
    assert response.data["email"] == valid_user_data["email"]


# Test Case 3: Invalid User Registration (Invalid Email)
@pytest.mark.django_db
def test_register_user_invalid_email(api_client, invalid_user_data):
    url = reverse("register_user")
    response = api_client.post(url, invalid_user_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


# Test Case 4: Missing Organization Data (Bad Request)
@pytest.mark.django_db
def test_register_organization_missing_data(api_client):
    url = reverse("register_org")
    invalid_data = {}
    response = api_client.post(url, invalid_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data
