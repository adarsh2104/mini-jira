import pytest
from rest_framework.test import APIClient
from rest_framework import status
from collaborations.models import ProjectInvitation, Project

from organizations.models import Organization
from django.urls import reverse

from mini_jira.models import User


@pytest.fixture
def user():
    # invite sender
    user = User.objects.create_user(
        username="johndoe",
        email="john@example.com",
        password="password123"
    )
    return user


@pytest.fixture
def user2():
    # invite receiver
    user2 = User.objects.create_user(
        username="jindoe",
        email="jindoe@example.com",
        password="password123"
    )
    return user2


@pytest.fixture
def user3():
    # invite receiver
    user3 = User.objects.create_user(
        username="jindoe",
        email="jindoe@example.com",
        password="password123"
    )
    return user3


@pytest.fixture
def organization():
    return Organization.objects.create(
        name="default_org",
    )


@pytest.fixture
def project(user, organization):
    project = Project.objects.create(
        name="Project A",
        description="Test project",
        created_by=user,
        organization=organization
    )
    return project


@pytest.fixture
def invitation(user, project, user2):
    invitation = ProjectInvitation.objects.create(
        project=project,
        inviter=user,
        email=user2.email,
        status=ProjectInvitation.STATUS_PENDING
    )
    return invitation


@pytest.fixture
def invitation_2(user, project, user3):
    invitation_2 = ProjectInvitation.objects.create(
        project=project,
        inviter=user,
        email=user3.email,
        status=ProjectInvitation.STATUS_PENDING
    )
    return invitation_2


@pytest.fixture
def client():
    return APIClient()


# Test Case: Send Invitation
@pytest.mark.django_db
def test_send_invite(client, user, project):
    client.force_authenticate(user=user)
    url = reverse("send_invite")
    data = {
        "project": str(project.id),
        "email": user.email
    }

    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["detail"] == "Invitation sent successfully."


# Test Case: Respond to Invitation - Accept
@pytest.mark.django_db
def test_respond_invite_accept(client, user2, invitation, project):
    client.force_authenticate(user=user2)
    url = reverse("respond_invite",  kwargs={"uid": invitation.id})
    data = {
        "project": project.id,
        "email": user2.email,
        "status": "ACCEPTED"
    }
    response = client.post(url, data, format="json")
    invitation.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert invitation.status == ProjectInvitation.STATUS_ACCEPTED
    assert invitation.responded_at is not None


# Test Case: Respond to Invitation - Reject
@pytest.mark.django_db
def test_respond_invite_reject(client, user3, invitation_2, project):
    client.force_authenticate(user=user3)
    url = reverse("respond_invite",  kwargs={"uid": invitation_2.id})
    data = {
        "project": project.id,
        "email": user3.email,
        "status": "REJECTED"
    }
    response = client.post(url, data, format="json")
    invitation_2.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert invitation_2.status == ProjectInvitation.STATUS_REJECTED
    assert invitation_2.responded_at is not None


# Test Case: Respond to Invitation - Not Found
@pytest.mark.django_db
def test_respond_invite_not_found(client, user):
    client.force_authenticate(user=user)
    url = reverse("respond_invite",  kwargs={"uid": 9999})
    data = {
        "status": "ACCEPTED"
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Invitation not found."


# Test Case: Get List of Invitations
@pytest.mark.django_db
def test_list_invites(client, user2, invitation):
    client.force_authenticate(user=user2)
    url = reverse("list_invites")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == invitation.id
    assert response.data[0]["status"] == invitation.status
    assert response.data[0]["project_name"] == str(invitation.project.name)
