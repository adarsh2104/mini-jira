
from rest_framework.permissions import IsAuthenticated
from projects.models import Project
from mini_jira import constants


class ProjectCollaboratorPermission(IsAuthenticated):
    message = "Permission denied"

    def has_permission(self, request, view):
        method = request.method
        user_group = request.user.groups.all().first()

        if method == "DELETE" and (
            not user_group or (user_group and user_group.name != constants.ADMIN)
        ):
            return False

        project = Project.objects.filter(id=view.kwargs.get("project_uuid")).first()
        if not project:
            return True

        if project.is_collaborator(user=request.user):
            return True
        return False
