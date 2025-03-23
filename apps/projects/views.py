from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from projects.models import Project
from projects.serializers import ProjectListSerializer, ProjectCreateSerializer, ProjectDetailSerializer
from rest_framework.generics import ListAPIView
from projects.permissions import ProjectCollaboratorPermission


class ProjectListView(ListAPIView):
    permission_classes = [ProjectCollaboratorPermission,]

    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # def get(self, request):
    #     projects = Project.objects.all()

    #     paginator = PageNumberPagination()
    #     paginator.page_size = 10
    #     paginated_projects = paginator.paginate_queryset(projects, request)
    #     serializer = ProjectListSerializer(paginated_projects, many=True)
    #     return paginator.get_paginated_response(serializer.data)

    # def get(self, request):
    #     order_by = request.query_params.get('order_by', '-created_at')
    #     search = request.query_params.get('search', '')

    #     # Filtering Projects based on search query (if any)
    #     projects = Project.objects.filter(
    #         Q(name__icontains=search) |
    #         Q(description__icontains=search)
    #     ).order_by(order_by)

    #     # Pagination setup
    #     paginator = PageNumberPagination()
    #     paginator.page_size = 10  # Or set to whatever you'd like
    #     paginated_projects = paginator.paginate_queryset(projects, request)

    #     # Serialize paginated results
    #     serializer = ProjectSerializer(paginated_projects, many=True)

    #     # Return paginated response
    #     return paginator.get_paginated_response(serializer.data)


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


