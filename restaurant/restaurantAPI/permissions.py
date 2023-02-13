from rest_framework import permissions

class managerGroupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return True

class deliveryGroupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser or request.user.groups.filter(name='Delivery crew').exists():
            return True