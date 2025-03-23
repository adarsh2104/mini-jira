
from rest_framework.permissions import IsAuthenticated

from tasks.models import Task


class TaskCollaboratorPermission(IsAuthenticated):
    message = "Permission denied"

    def has_permission(self, request, view):
        method = request.method
        task = Task.objects.filter(id=view.kwargs.get("uuid")).first()
        if not task:
            return True

        if method in ["DELETE", "PUT"]:
            if task.is_collaborator(user=request.user):
                return True
            return False

        if task.project.is_collaborator(user=request.user):
            return True
        return False
