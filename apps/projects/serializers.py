from rest_framework import serializers
from projects.models import Project
# from accounts.serializers import UserSerializer
from mini_jira.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ProjectListSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "created_by",
            "created_at",
            "members",
            "updated_at"
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    members = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        many=True,
        slug_field="username",
        required=False
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "members",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]

    def get_request_user(self):
        return self.context.get("request").user

    def get_organization_id(self, user=None):
        if not user:
            user = self.get_request_user()
        org = user.organizations_organization.first()
        return getattr(org, "id", None)

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        user = self.get_request_user()
        validated_data["created_by"] = user
        validated_data["organization_id"] = self.get_organization_id(user)
        instance = super().create(validated_data)
        instance.members.set(members)
        instance.members.add(user)
        return instance

    def update(self, instance, validated_data):
        members = validated_data.pop("members", [])
        user = self.get_request_user()
        validated_data["created_by"] = user
        validated_data["organization_id"] = self.get_organization_id(user)
        instance = super().update(instance, validated_data)
        if members:
            instance.members.clear()
            instance.members.set(members)
            instance.members.add(user)
        return instance


class ProjectDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "created_by",
            "modified_by",
            "members",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "modified_by"
        ]

    def get_request_user(self):
        return self.context.get("request").user

    def get_organization_id(self, user=None):
        if not user:
            user = self.get_request_user()
        org = user.organizations_organization.first()
        return getattr(org, "id", None)

    def create(self, validated_data):
        user = self.get_request_user()
        validated_data["created_by"] = user
        validated_data["organization_id"] = self.get_organization_id(user)
        return super().create(validated_data)

    # def update(self, instance, validated_data):
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance
