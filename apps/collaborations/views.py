from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from collaborations.serializers import ProjectInvitationCreateSerializer, ProjectInvitationResponseSerializer, ProjectInvitationListSerializer
from collaborations.models import ProjectInvitation
from django.utils import timezone


class ProjectInvitationListView(APIView):
    def get(self, request):
        invitations = ProjectInvitation.objects.filter(email=request.user.email)
        serializer = ProjectInvitationListSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectInvitationCreateView(APIView):
    def post(self, request):
        serializer = ProjectInvitationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(inviter=request.user)
            return Response({"detail": "Invitation sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectInvitationResponseView(APIView):
    def get_object(self, uid, user):
        try:
            return ProjectInvitation.objects.get(id=uid, email=user.email)
        except ProjectInvitation.DoesNotExist:
            return None

    def post(self, request, uid):
        invitation = self.get_object(uid, request.user)
        if invitation:
            serializer = ProjectInvitationResponseSerializer(invitation, data=request.data)
            if serializer.is_valid():
                serializer.save(responded_at=timezone.now())
                return Response({"detail": "Invitation response recorded."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Invitation not found."}, status=status.HTTP_404_NOT_FOUND)