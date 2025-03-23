from django.urls import path
from projects.views import ProjectListView, ProjectDetailView, ProjectCreateView


urlpatterns = [
    path("list/", ProjectListView.as_view(), name="project_list"),
    path("create/", ProjectCreateView.as_view(), name="project_create"),
    path("detail/<uuid:uuid>", ProjectDetailView.as_view(), name="project_detail"),
]
