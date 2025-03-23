from django.conf import settings

from rest_framework import serializers

from projects.models import Project
from tasks.models import Task, TaskDiscussion, TaskDiscussionMessage, TaskComment
from mini_jira.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class TaskListSerializer(serializers.ModelSerializer):
    assignee = serializers.StringRelatedField()
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assignee",
            "due_date",
            "status",
            "completed",
            "priority",
            "created_by",
            "modified_by",
            "created_at",
            "updated_at",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):

    description = serializers.CharField(required=False, allow_blank=True)
    assignee = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        required=False,
        allow_null=True
    )
    priority = serializers.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        error_messages={
            "invalid_choice": (
                f"""Invalid priority selected. Please choose from: {
                    ', '.join([obj[0] for obj in Task.PRIORITY_CHOICES])
                }"""
            )
        },
        required=False,
        allow_null=True
    )
    status = serializers.ChoiceField(
        choices=Task.STATUS_CHOICES,
        error_messages={
            "invalid_choice": (
                f"""Invalid status selected. Please choose from: {
                    ', '.join([obj[0] for obj in Task.STATUS_CHOICES])
                }"""
            )
        },
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assignee",
            "due_date",
            "priority",
            "status",
            "project",
            "completed",
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
        ]

    def validate_assignee(self, value):
        if value:
            project = Project.objects.filter(
                id=self.initial_data.get("project")
            ).first()
            if not project.is_collaborator(value):
                raise serializers.ValidationError(
                    {
                        "assignee": "Assignee must be from Project members"
                    }
                )
        return value


class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer()
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assignee",
            "due_date",
            "priority",
            "status",
            "project",
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
        ]

    @property
    def data(self):
        data = super().data
        data["project"] = str(data["project"])
        return data


class TaskDiscussionMessageSerializer(serializers.ModelSerializer):
    reply_of = serializers.SlugRelatedField(slug_field="text", read_only=True)
    created_by = serializers.SlugRelatedField(slug_field="username", read_only=True)
    modified_by = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = TaskDiscussionMessage
        fields = '__all__'


class TaskDiscussionSerializer(serializers.ModelSerializer):
    messages = TaskDiscussionMessageSerializer(many=True)

    class Meta:
        model = TaskDiscussion
        fields = '__all__'


class TaskDiscussionCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)

    class Meta:
        model = TaskDiscussion
        fields = ["id", "task", "title"]


class CommentSerializer(serializers.ModelSerializer):

    def validate_content(self, value):
        if self.instance:
            if not self.instance.is_content_editable:
                raise serializers.ValidationError(
                    {
                        "content": f"Comment cannot be edited after {int(settings.COMMENT_EDIT_DURATION_SECONDS/60)} mins"
                    }
                )
        return value

    class Meta:
        model = TaskComment
        fields = "__all__"


class TaskCommentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)

    class Meta:
        model = Task
        fields = "__all__"