# logging_management/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import LogListSerializer, LogDetailSerializer, LogCreateSerializer
from .models import Log

from accounts.permissions import RoleBasedPermission

class LogListView(generics.ListAPIView):
    queryset = Log.objects.all().order_by('-action_started_at')
    serializer_class = LogListSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    throttle_scope = 'logs'


class LogDetailView(generics.RetrieveAPIView):
    queryset = Log.objects.all()
    serializer_class = LogDetailSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    throttle_scope = 'logs'


class LogCreateView(generics.CreateAPIView):
    queryset = Log.objects.all()
    serializer_class = LogCreateSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    throttle_scope = 'logs'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        log = serializer.save()
        return Response(LogDetailSerializer(log).data, status=status.HTTP_201_CREATED)
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
