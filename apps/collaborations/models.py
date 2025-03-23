from django.db import models

from invitations.models import Invitation
from projects.models import Project


class ProjectInvitation(Invitation):
    STATUS_PENDING = "PENDING"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    )

    project = models.ForeignKey(Project, related_name='invitations', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation to {self.inviter} for project {self.project.name} ({self.status})"
