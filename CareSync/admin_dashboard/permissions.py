from django.contrib.auth.models import Permission

class ViewDashboardPermission(Permission):
    def has_permission(self, request, view):
        return request.user.is_staff