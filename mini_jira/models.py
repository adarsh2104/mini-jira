import threading
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, "user", None)


def set_current_user(user):
    _thread_locals.user = user


class AbstractUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseTimeStampedModel(AbstractUUIDModel):
    created_by = models.ForeignKey(
        User,
        related_name="%(class)s_created_by",
        on_delete=models.CASCADE
    )
    modified_by = models.ForeignKey(
        User,
        related_name="%(class)s_modified_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            self.modified_by = user
            if "update_fields" in kwargs and "modified_by" not in kwargs["update_fields"]:
                kwargs["update_fields"].append("modified_by")
        super(BaseTimeStampedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
