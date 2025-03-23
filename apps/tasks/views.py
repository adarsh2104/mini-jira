from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project
from projects.permissions import ProjectCollaboratorPermission
from tasks.models import Task, TaskComment, TaskDiscussion
from tasks.serializers import (
    TaskListSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskDiscussionSerializer,
    TaskDiscussionCreateSerializer,
    TaskCommentSerializer
)
from tasks.permissions import TaskCollaboratorPermission


class TaskListView(APIView):
    permission_classes = [ProjectCollaboratorPermission,]

    def get_project_object(self, uuid):
        try:
            return Project.objects.get(id=uuid)
        except Project.DoesNotExist:
            return None

    def get(self, request, project_uuid):
        project = self.get_project_object(project_uuid)
        if project:
            tasks = Task.objects.filter(project=project, is_active=True)
            serializer = TaskListSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)


class TaskCreateView(APIView):
    permission_classes = [ProjectCollaboratorPermission,]

    def get_project_object(self, uuid):
        try:
            return Project.objects.get(id=uuid)
        except Project.DoesNotExist:
            return None

    def post(self, request, project_uuid):
        project = self.get_project_object(project_uuid)
        if project:
            data = {**request.data, "project": project.id}
            serializer = TaskCreateSerializer(data=data, context={"request": request})
            if serializer.is_valid():
                serializer.save(created_by=request.user, modified_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)


class TaskDetailView(APIView):
    permission_classes = [TaskCollaboratorPermission,]

    def get_object(self, uuid):
        try:
            return Task.objects.get(id=uuid, is_active=True)
        except Task.DoesNotExist:
            return None

    def get(self, request, uuid):
        instance = self.get_object(uuid)
        if instance:
            serializer = TaskDetailSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, uuid):
        instance = self.get_object(uuid)
        if instance:
            data = {**request.data, "project": instance.project.id}
            serializer = TaskCreateSerializer(
                instance,
                data=data,
                context={"request": request},
                partial=True
            )
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, uuid):
        instance = self.get_object(uuid)
        if instance:
            instance.delete_object()
            return Response(status=status.HTTP_200_OK)
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


class TaskDiscussionView(APIView):
    permission_classes = [TaskCollaboratorPermission,]

    def get_task_object(self, uuid):
        try:
            return Task.objects.get(id=uuid, is_active=True)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_uuid):
        discussions = TaskDiscussion.objects.filter(task=task_uuid)
        serializer = TaskDiscussionSerializer(discussions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_uuid):
        task = self.get_task_object(task_uuid)
        if task:
            data = {**request.data, "task": task.id}
            serializer = TaskDiscussionCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, modified_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


class TaskCommentView(APIView):
    permission_classes = [TaskCollaboratorPermission,]

    def get_task_object(self, uuid):
        try:
            return Task.objects.get(id=uuid, is_active=True)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_uuid):
        instance = self.get_task_object(task_uuid)
        serializer = TaskCommentSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentMarkAsReadView(APIView):
    permission_classes = [TaskCollaboratorPermission,]

    def get_object(self, uuid):
        try:
            return TaskComment.objects.get(id=uuid)
        except TaskComment.DoesNotExist:
            return None

    def post(self, request, comment_uuid):
        instance = self.get_object(comment_uuid)
        if instance:
            instance.mark_as_read(request.user)
            return Response(status=status.HTTP_200_OK)
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
