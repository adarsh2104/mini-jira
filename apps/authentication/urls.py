from django.urls import path
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path("jwt/generate-token/", jwt_views.TokenObtainPairView.as_view(), name="generate_token"),
    path("jwt/refresh-token/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
