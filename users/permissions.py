from rest_framework.permissions import BasePermission
from users.models import Role  # Role modelingizni import qiling



class UserPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        # 1. Foydalanuvchi autentifikatsiya qilinganmi?
        if not user or not user.is_authenticated:
            return request.method in ["GET", "HEAD", "OPTIONS"]

        user_role = getattr(user, "role_user", "").upper()

        if user_role == Role.VRACH:
            return True

        if user_role == Role.TTB:
            return request.method != "POST"

        if user_role in [Role.VSSB, Role.BOSH_M, Role.VAZIR]:
            return request.method not in ["POST", "DELETE"]

        return request.method in ["GET", "HEAD", "OPTIONS"]
