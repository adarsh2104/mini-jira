from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from tasks.views import TaskDetailSerializer
from tasks.consumers import TaskUpdateConsumer


@receiver(post_save, sender=Task)
def task_update_handler(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    serializer = TaskDetailSerializer(instance)
    async_to_sync(channel_layer.group_send)(
        TaskUpdateConsumer.get_group_name(instance.id),
        {
            "type": TaskUpdateConsumer.EVENT_TYPE_TASK_UPDATE,
            "data": serializer.data
        }
    )
