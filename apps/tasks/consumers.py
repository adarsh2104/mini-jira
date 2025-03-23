from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from tasks.models import TaskComment, TaskDiscussionMessage
from tasks.serializers import CommentSerializer, TaskDiscussionMessageSerializer, TaskCommentSerializer
from mini_jira.models import User


class TaskUpdateConsumer(AsyncJsonWebsocketConsumer):
    GROUP_NAME = "task_{task_uuid}_group"

    EVENT_TYPE_TASK_UPDATE = "task_update"
    EVENT_TYPE_DISCUSSION_UPDATE = "discussion_update"
    EVENT_TYPE_COMMENT_UPDATE = "comment_update"

    @classmethod
    def get_group_name(cls, uuid):
        return cls.GROUP_NAME.format(task_uuid=uuid)

    async def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = self.get_group_name(self.uuid)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        event_type = content["type"]
        data = content["data"]

        if event_type == self.EVENT_TYPE_TASK_UPDATE:
            await self.handle_task_update(data)
        elif event_type == self.EVENT_TYPE_COMMENT_UPDATE:
            await self.handle_comment_update(data)
        elif event_type == self.EVENT_TYPE_DISCUSSION_UPDATE:
            await self.handle_discussion_update(data)

    async def handle_task_update(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": self.EVENT_TYPE_TASK_UPDATE,
                "data": data,
                "errors": None
            }
        )

    async def task_update(self, event):
        await self.send_json(event)

    async def handle_discussion_update(self, data):
        instance = await self.create_discussion_message(data)
        serializer = TaskDiscussionMessageSerializer(instance)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": self.EVENT_TYPE_DISCUSSION_UPDATE,
                "data": serializer.data,
                "errors": None
            }
        )

    async def discussion_update(self, event):
        await self.send_json(event)

    @database_sync_to_async
    def create_discussion_message(self, data):
        message = data["message"]
        user = User.objects.get(username=message["created_by"])
        return TaskDiscussionMessage.objects.create(
            discussion_id=data["id"],
            text=message["text"],
            created_by=user,
        )

    async def handle_comment_update(self, data):
        instance, errors = await self.create_or_update_comment(data)
        if errors:
            message_data = None
        if instance:
            serializer = CommentSerializer(instance)
            message_data = serializer.data
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": self.EVENT_TYPE_COMMENT_UPDATE,
                "data": message_data,
                "errors": errors
            }
        )

    @database_sync_to_async
    def create_or_update_comment(self, data):
        errors = None
        message = data["message"]
        user = User.objects.get(username=message["created_by"])
        comment_id = message.get("id")
        if comment_id:
            data = {
                "task": data["id"],
                "content": message["content"],
                "created_by_id": user.id,
            }
            instance = TaskComment.objects.get(id=comment_id)
            serializer = CommentSerializer(instance, data=data)
            if serializer.is_valid():
                serializer.save()
            return None, serializer.errors
        data = {
                "task_id": data["id"],
                "content": message["content"],
                "created_by": user,
            }
        return TaskComment.objects.create(**data), errors

    async def comment_update(self, event):
        await self.send_json(event)


