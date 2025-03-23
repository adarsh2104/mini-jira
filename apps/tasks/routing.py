from django.urls import path

from tasks import consumers

websocket_urlpatterns = [
    path("ws/task/<uuid:uuid>/updates", consumers.TaskUpdateConsumer.as_asgi()),
]