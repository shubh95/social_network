"""
URL configuration for social_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from accounts.views import UserRegisterView, UserLoginView, UserSearchView, BlockedUserListView, BlockedUserCreateView, UnblockedUserView
from friend_management.views import FriendRequestSendView, FriendRequestAcceptView, FriendRequestRejectView, FriendRequestListView, FriendListView
from logging_management.views import LogListView, LogCreateView, LogDetailView

from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Your API Title",
      default_version='v1',
      description="Self-describing API documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourapi.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('send_friend_request/', FriendRequestSendView.as_view(), name='send_friend_request'),
    path('accept_friend_request/', FriendRequestAcceptView.as_view(), name='accept_friend_request'),
    path('reject_friend_request/', FriendRequestRejectView.as_view(), name='reject_friend_request'),
    path('friend_requests/', FriendRequestListView.as_view(), name='friend_requests'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('blocked_users/', BlockedUserListView.as_view(), name='blocked_users'),
    path('block_user/', BlockedUserCreateView.as_view(), name='block_user'),
    path('unblock_user/', UnblockedUserView.as_view(), name='unblock_user'),
    path('logs/', LogListView.as_view(), name='logs'),
    path('logs/create/', LogCreateView.as_view(), name='create_log'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc
]
