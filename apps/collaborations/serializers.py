from rest_framework import serializers
from collaborations.models import ProjectInvitation


class ProjectInvitationListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name")
    status = serializers.CharField()

    class Meta:
        model = ProjectInvitation
        fields = ["id", "project_name", "status", "responded_at"]


class ProjectInvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvitation
        fields = ["project", "email", "inviter"]


class ProjectInvitationResponseSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=ProjectInvitation.STATUS_CHOICES,
        error_messages={
            "invalid_choice": (
                f"""Invalid status selected. Please choose from: {
                ProjectInvitation.STATUS_ACCEPTED,ProjectInvitation.STATUS_REJECTED
                }"""
            )
        },
        required=True
    )

    def validate_status(self, value):
        if self.instance and self.instance.status != ProjectInvitation.STATUS_PENDING:
            raise serializers.ValidationError({"status": f"Invite is already {self.instance.status.title()}"})
        return value

    class Meta:
        model = ProjectInvitation
        fields = ["status", "responded_at"]
