from rest_framework import permissions
from .models import BlockedUser

class BaseBlocklistPermission(permissions.BasePermission):

    def get_user_id(self, request, view):
        return view.kwargs.get('user_id')

    def has_permission(self, request, view):
        request_user = request.user
        accessed_user_id = self.get_user_id(request, view)
        if accessed_user_id is None:
            return False
        
        try:
            accessed_user_id = int(accessed_user_id)
        except ValueError:
            return False
        
        is_blocked = BlockedUser.objects.filter(user=accessed_user_id, blocked_user=request_user).exists()

        return not is_blocked


class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Define role-based permissions for each action
        role_permissions = {
            'GET': ['read', 'write', 'admin'],
            'POST': ['write', 'admin'],
            'PUT': ['write', 'admin'],
            'PATCH': ['write', 'admin'],
            'DELETE': ['admin']
        }

        # Get the roles allowed to perform the action
        roles_allowed = role_permissions.get(request.method, [])

        # Check if the user has any of the allowed roles
        request_user_role = request.user.role
        return request_user_role in roles_allowed


def create_blocklist_permissions(get_user_id):
    class BlocklistPermission(BaseBlocklistPermission):

        def get_user_id(self, request, view):
            return get_user_id(request, view)

    return BlocklistPermission
