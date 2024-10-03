# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, BlockedUser
from .serializers import UserSerializer, UserLoginSerializer, UserSignupSerializer, BlockedUserListSerializer, BlockedUserCreateSerializer, MyselfSerializer
from .permissions import RoleBasedPermission


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    throttle_scope = 'register'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(MyselfSerializer(user).data, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': MyselfSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserSearchView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    throttle_scope = 'search'

    def get_queryset(self):
        request_user = self.request.user
        queryset = super().get_queryset().exclude(
            id=request_user.id
        ).exclude(
            id__in=request_user.blocked_by.all().values_list('user_id', flat=True)
        ).search(self.request.query_params.get('q', ''))
        return queryset
    
    def get_serializer_context(self):
        return {'request_user': self.request.user}


class BlockedUserListView(generics.ListAPIView):
    queryset = BlockedUser.objects.all()
    serializer_class = BlockedUserListSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class BlockedUserCreateView(generics.CreateAPIView):
    queryset = BlockedUser.objects.all()
    serializer_class = BlockedUserCreateSerializer
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


class UnblockedUserView(generics.DestroyAPIView):
    queryset = BlockedUser.objects.all()
    permission_classes = (permissions.IsAuthenticated, RoleBasedPermission)

    def get_object(self):
        return self.queryset.get(user=self.request.user, blocked_user_id=self.kwargs['blocked_user_id'])
