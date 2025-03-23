from django.db import models

from organizations.models import Organization

from mini_jira.models import BaseTimeStampedModel, User


class Project(BaseTimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(Organization, related_name="projects", on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="projects")

    def __str__(self):
        return self.name

    def is_collaborator(self, user):
        return self.members.filter(id=user.id).exists()
