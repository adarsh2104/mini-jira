from rest_framework import serializers
from mini_jira.models import User
from organizations.models import Organization
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import Group


class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=Organization.objects.all(),
                message=_("Organization name already in use")
            )
        ]
    )

    class Meta:
        model = Organization
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    USER_GROUP_CHOICES = tuple(
        (name, name) for name in settings.ALLOWED_USER_GROUPS
    )

    password = serializers.CharField(write_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Organization.objects.all(),
        error_messages={
            "does_not_exist": (
                _("Organization ID does not exist.")
            )
        },
    )
    user_group = serializers.SlugRelatedField(
        queryset=Group.objects.all(),
        write_only=True,
        slug_field="name",
        error_messages={
            "does_not_exist": (
                _(f"Invalid value.Options are: {settings.ALLOWED_USER_GROUPS}")
            )
        },
    )
    profile_picture = serializers.ImageField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "password",
            "user_group",
            "organization_id",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user_group = validated_data.pop("user_group")
        organization = validated_data.pop("organization_id")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        user.organizations_organization.add(organization)
        user.groups.add(user_group)
        return user
