from rest_framework.permissions import BasePermission

from ebos2206.models.m06_emp_mas import T06Emp10


class IsEmployeeSelfService(BasePermission):
    """
    Check if authenticated user is an employee
    """

    def has_permission(self, request, view):
        try:
            T06Emp10.objects.get(employee_code=request.user.username)
            return request.user.is_authenticated is True
        except T06Emp10.DoesNotExist:
            return False
