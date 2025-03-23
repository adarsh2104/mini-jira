from django.conf import settings
from django.db import models
from django.utils import timezone

from projects.models import Project
from mini_jira.models import BaseTimeStampedModel, User


class Task(BaseTimeStampedModel):
    STATUS_TODO = "TODO"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_DONE = "DONE"
    STATUS_CHOICES = [
        (STATUS_TODO, "To Do"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
    ]

    PRIORITY_LOW = "Low"
    PRIORITY_Medium = "Medium"
    PRIORITY_High = "High"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, PRIORITY_LOW),
        (PRIORITY_Medium, PRIORITY_Medium),
        (PRIORITY_High, PRIORITY_High),
    ]

    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignee = models.ForeignKey(User, related_name="tasks", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    due_date = models.DateTimeField(null=True, blank=True, default=None)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def delete_object(self):
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def is_collaborator(self, user):
        return self.created_by.id == user.id or self.assignee.id == user.id


class TaskComment(BaseTimeStampedModel):
    task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    reply_of = models.ForeignKey(
        "self",
        related_name="replies",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    is_editable = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.created_by.username} on {self.task}"

    class Meta:
        ordering = ['created_at']

    def _set_is_editable(self, value):
        self.is_editable = False
        self.save(update_fields=["is_editable"])

    @property
    def is_content_editable(self):
        secs_elapsed = (timezone.now() - self.created_at).total_seconds()
        if self.is_editable and secs_elapsed > settings.COMMENT_EDIT_DURATION_SECONDS:
            self._set_is_editable(False)
        return self.is_editable

    def mark_as_read(self, user):
        return self.read_receipts.get_or_create(user=user)


class CommentReadReceipt(models.Model):
    task_comment = models.ForeignKey(TaskComment, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_receipts')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("task_comment", "user")

    def __str__(self):
        return f"User {self.user.username} read comment {self.task_comment.id} at {self.read_at}"


class TaskDiscussion(BaseTimeStampedModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    task = models.ForeignKey(Task, related_name="task_discussions", on_delete=models.CASCADE)

    def __str__(self):
        return f"Discussion on Task {self.task.title} by {self.created_by.username}"

    class Meta:
        ordering = ['-created_at']


class TaskDiscussionMessage(BaseTimeStampedModel):
    discussion = models.ForeignKey(TaskDiscussion, related_name="messages", on_delete=models.CASCADE)
    text = models.TextField()
    reply_of = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    is_editable = models.BooleanField(default=True)

    def __str__(self):
        return f"Message by {self.created_by.username} in {self.discussion.title}"

    class Meta:
        ordering = ['-created_at']
