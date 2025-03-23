import pytest
import uuid
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from projects.models import Project

from organizations.models import Organization
from django.contrib.auth.models import Group

from mini_jira.models import User


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
    admin_user_group, _ = Group.objects.get_or_create(
        name="Admin",
    )
    return admin_user_group

@pytest.fixture
def user(api_client, organization, admin_user_group):
    """Fixture to create a user and authenticate for the tests."""
    user = User.objects.create_user(username="johndoe", email="johndoe@example.com", password="password123")
    user.organizations_organization.add(organization)
    user.groups.add(admin_user_group)
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def member_user():
    """Fixture to create a user and authenticate for the tests."""
    member_user = User.objects.create_user(username="janedoe", email="janedoe@example.com", password="password123")
    return member_user


@pytest.fixture
def project(user, member_user, organization):
    """Fixture to create a project associated with a user."""
    project = Project.objects.create(
        name="Test Project",
        description="Test project description",
        created_by=user,
        modified_by=user,
        organization_id=organization.id
    )
    project.members.add(member_user)
    return project


# Test Case 1: List Projects
@pytest.mark.django_db
def test_project_list(api_client, user):
    url = reverse("project_list")  # Resolves to /projects/list/
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


# Test Case 2: Create Project
@pytest.mark.django_db
def test_project_create(api_client, user):
    url = reverse("project_create")
    data = {
        "name": "New Project",
        "description": "New project description",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == data["name"]
    assert response.data["description"] == data["description"]


# Test Case 3: Get Project Detail
@pytest.mark.django_db
def test_project_detail(api_client, user, project):
    url = reverse("project_detail", kwargs={"uuid": project.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == project.name
    assert response.data["description"] == project.description
    assert response.data["members"][0]["username"] == project.members.all().first().username


# Test Case 4: Get Project Detail (Project Not Found)
@pytest.mark.django_db
def test_project_detail_not_found(api_client, user):
    url = reverse("project_detail", kwargs={"uuid": uuid.uuid4()})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Project not found."


# Test Case 5: Update Project
@pytest.mark.django_db
def test_project_update(api_client, user, project):
    url = reverse("project_detail", kwargs={"uuid": project.id})
    data = {
        "name": "Updated Project",
        "description": "Updated project description",
    }
    response = api_client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data["name"]
    assert response.data["description"] == data["description"]


# Test Case 6: Update Project (Project Not Found)
@pytest.mark.django_db
def test_project_update_not_found(api_client, user):
    url = reverse("project_detail", kwargs={"uuid": uuid.uuid4()})
    data = {
        "title": "Updated Project",
        "description": "Updated project description",
    }
    response = api_client.put(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Project not found."


# Test Case 7: Delete Project
@pytest.mark.django_db
def test_project_delete(api_client, user, project):
    url = reverse("project_detail", kwargs={"uuid": project.id})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert Project.objects.filter(id=project.id).count() == 0


# Test Case 8: Delete Project (Project Not Found)
@pytest.mark.django_db
def test_project_delete_not_found(api_client, user):
    url = reverse("project_detail", kwargs={"uuid": uuid.uuid4()})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Project not found."
