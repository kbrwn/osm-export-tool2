"""Provides custom permissions for API endpoints."""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission which restricts delete and update
    operations on models to the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsHDXAdmin(permissions.BasePermission):
    """Custom permission which restricts operations to HDX admins."""

    def has_permission(self, request, view): # noqa
        return request.user.has_perms((
            'jobs.add_hdxexportregion',
            'jobs.change_hdxexportregion',
            'jobs.delete_hdxexportregion',
        ))
