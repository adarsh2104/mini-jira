from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project
from projects.serializers import ProjectListSerializer, ProjectCreateSerializer, ProjectDetailSerializer
from projects.permissions import ProjectCollaboratorPermission


class ProjectListView(ListAPIView):
    permission_classes = [ProjectCollaboratorPermission,]

    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectCreateView(APIView):
    permission_classes = [ProjectCollaboratorPermission,]

    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(created_by=request.user, modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = [ProjectCollaboratorPermission,]

    def get_object(self, uuid):
        try:
            return Project.objects.get(id=uuid)
        except Project.DoesNotExist:
            return None

    def get(self, request, uuid):
        instance = self.get_object(uuid)
        if instance:
            serializer = ProjectDetailSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, uuid):
        instance = self.get_object(uuid)
        if instance:
            serializer = ProjectCreateSerializer(
                instance,
                data=request.data,
                context={"request": request},
                partial=True,
            )
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, uuid):
        instance = self.get_object(uuid)
        if instance:
            instance.delete()
            return Response(status=status.HTTP_200_OK)
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)


