import pytest
import uuid
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from projects.models import Project

from organizations.models import Organization
from django.contrib.auth.models import Group

from mini_jira.models import User



import pytest
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from tasks.models import Task, TaskComment, TaskDiscussion
from projects.models import Project

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
def project(user, organization):
    """Fixture to create a project associated with a user."""
    project = Project.objects.create(
        name="Test Project",
        description="Test project description",
        created_by=user,
        modified_by=user,
        organization_id=organization.id
    )
    project.members.add(user)
    return project


@pytest.fixture
def task(user, project):
    """Fixture to create a task associated with a user and project."""
    return Task.objects.create(
        title="Test Task",
        description="Test task description",
        project=project,
        created_by=user,
        modified_by=user,
    )


# Test Case 1: List Tasks for a Project
@pytest.mark.django_db
def test_task_list(api_client, user, project):
    url = reverse("task_list", kwargs={"project_uuid": project.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


# Test Case 2: Create Task for a Project
@pytest.mark.django_db
def test_task_create(api_client, user, project):
    url = reverse("task_create", kwargs={"project_uuid": project.id})  # Resolves to /tasks/create/{project_uuid}/
    data = {
        "title": "New Task",
        "description": "New task description",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == data["title"]
    assert response.data["description"] == data["description"]


# Test Case 3: Get Task Detail
@pytest.mark.django_db
def test_task_detail(api_client, user, task):
    url = reverse("task_detail", kwargs={"uuid": task.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == task.title
    assert response.data["description"] == task.description


# Test Case 4: Get Task Detail (Task Not Found)
@pytest.mark.django_db
def test_task_detail_not_found(api_client, user):
    url = reverse("task_detail", kwargs={"uuid": uuid.uuid4()})  # Non-existing task UUID
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Task not found."


# Test Case 5: Update Task
@pytest.mark.django_db
def test_task_update(api_client, user, task):
    url = reverse("task_detail", kwargs={"uuid": task.id})  # Resolves to /tasks/detail/{uuid}/
    data = {
        "title": "Updated Task",
        "description": "Updated task description",
    }
    response = api_client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == data["title"]
    assert response.data["description"] == data["description"]


# Test Case 6: Update Task (Task Not Found)
@pytest.mark.django_db
def test_task_update_not_found(api_client, user):
    url = reverse("task_detail", kwargs={"uuid": uuid.uuid4()})  # Non-existing task UUID
    data = {
        "title": "Updated Task",
        "description": "Updated task description",
    }

    response = api_client.put(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Task not found."


# Test Case 7: Delete Task
@pytest.mark.django_db
def test_task_delete(api_client, user, task):
    url = reverse("task_detail", kwargs={"uuid": task.id})  # Resolves to /tasks/detail/{uuid}/
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert Task.objects.filter(id=task.id).count() != 0  # Ensure the task was deleted
    assert Task.objects.filter(id=task.id, is_active=True).count() == 0


# Test Case 8: Delete Task (Task Not Found)
@pytest.mark.django_db
def test_task_delete_not_found(api_client, user):
    url = reverse("task_detail", kwargs={"uuid": uuid.uuid4()})  # Non-existing task UUID
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Task not found."


# Test Case 9: Get Task Discussions
@pytest.mark.django_db
def test_task_discussions(api_client, user, task):
    url = reverse("task_discussion", kwargs={"task_uuid": task.id})  # Resolves to /tasks/discussions/{task_uuid}/
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)  # Should return a list of task discussions


# Test Case 10: Create Task Discussion
@pytest.mark.django_db
def test_task_discussion_create(api_client, user, task):
    url = reverse("task_discussion", kwargs={"task_uuid": task.id})  # Resolves to /tasks/discussions/{task_uuid}/
    data = {
        "title": "New discussion"
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == data["title"]


# Test Case 11: Get Task Comments
@pytest.mark.django_db
def test_task_comments(api_client, user, task):
    url = reverse("task_comments", kwargs={"task_uuid": task.id})  # Resolves to /tasks/comments/{task_uuid}/
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data["comments"], list)  # Should return a list of task comments


# Test Case 12: Mark Task Comment as Read
@pytest.mark.django_db
def test_task_comment_mark_as_read(api_client, user, task):
    # Create a task comment first
    comment = TaskComment.objects.create(
        task=task,
        created_by=user,
        content="Test comment",
    )
    url = reverse("task_comments", kwargs={"comment_uuid": comment.id})
    response = api_client.post(url)

    comment.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK


# Test Case 13: Mark Task Comment as Read (Comment Not Found)
@pytest.mark.django_db
def test_task_comment_mark_as_read_not_found(api_client, user):
    url = reverse("task_comments", kwargs={"comment_uuid": uuid.uuid4()})  # Non-existing comment UUID

    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Comment not found."

