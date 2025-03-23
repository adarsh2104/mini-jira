from django.urls import path

from collaborations.views import (
    ProjectInvitationCreateView,
    ProjectInvitationResponseView,
    ProjectInvitationListView
)

urlpatterns = [
    path("send-invite/", ProjectInvitationCreateView.as_view(), name="send_invite"),
    path("invite/respond/<int:uid>", ProjectInvitationResponseView.as_view(), name="respond_invite"),
    path("invite/list/", ProjectInvitationListView.as_view(), name="list_invites")
]
