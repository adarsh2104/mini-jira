from django.urls import path
from registration.views import RegisterUserView, RegisterOrganizationView

urlpatterns = [
    path("organization/", RegisterOrganizationView.as_view(), name="register_org"),
    path("user/", RegisterUserView.as_view(), name="register_user"),
]
