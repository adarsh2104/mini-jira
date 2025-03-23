from django.urls import path
from tasks.views import TaskListView, TaskDetailView, TaskCreateView, TaskDiscussionView, TaskCommentView


urlpatterns = [
    path("list/<uuid:project_uuid>", TaskListView.as_view(), name="task_list"),
    path("create/<uuid:project_uuid>", TaskCreateView.as_view(), name="task_create"),
    path("detail/<uuid:uuid>", TaskDetailView.as_view(), name="task_detail"),
    path("discussions/<uuid:task_uuid>", TaskDiscussionView.as_view(), name="task_discussion"),
    path("comments/<uuid:task_uuid>", TaskCommentView.as_view(), name="task_comments"),
    path("comments/<uuid:comment_uuid>/mark-as-read/", TaskCommentView.as_view(), name="task_comments"),
]
