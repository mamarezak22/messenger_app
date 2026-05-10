

from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request is a safe method (GET, HEAD, OPTIONS)
        if request.method in request.SAFE_METHODS:
            return True
        # Write permission is only allowed to the owner of the snippet
        return obj.owner == request.user
