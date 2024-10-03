# views.py
from accounts.serializers import UserSerializer
from friend_management.models import FriendRequest
from friend_management.serializers import FriendRequestSerializer
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from friend_management.utils import FriendshipManager
from accounts.models import CustomUser
from accounts.permissions import create_blocklist_permissions, RoleBasedPermission


class FriendRequestSendView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, create_blocklist_permissions(lambda request, view: request.data.get('to_user_id')),
                            RoleBasedPermission)

    throttle_scope = 'friend_requests'

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if FriendshipManager.send_friend_request(request.user, to_user):
            return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Friend request not sent'}, status=status.HTTP_400_BAD_REQUEST)


class FriendRequestAcceptView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    def post(self, request, *args, **kwargs):
        friend_request_id = request.data.get('friend_request_id')
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except FriendRequest.DoesNotExist:
            return Response({'message': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if friend_request.to_user != request.user:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        FriendshipManager.accept_friend_request(friend_request)

        return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)


class FriendRequestRejectView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    def post(self, request, *args, **kwargs):
        friend_request_id = request.data.get('friend_request_id')
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except FriendRequest.DoesNotExist:
            return Response({'message': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if friend_request.to_user != request.user:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        FriendshipManager.reject_friend_request(friend_request)

        return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)


class FriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    VALID_SORT_FIELDS = ['from_user__name', 'created_at', '-from_user__name', '-created_at']

    def get_queryset(self):
        if 'sort' in self.request.query_params:
            sort = self.request.query_params['sort']
            if sort not in self.VALID_SORT_FIELDS:
                # error invalid  sort field
                raise ValidationError({'sort': 'Invalid sort field'})
        else:
            sort = 'created_at'
            
        return FriendshipManager.get_friend_requests(self.request.user, sort)


class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    def get_queryset(self):
        return FriendshipManager.get_friends(self.request.user)

