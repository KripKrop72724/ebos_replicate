from typing import Dict

from django.contrib.auth.models import Permission
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ebos2201.exceptions import ExpiredOtpException, InvalidOtpException
from ebos2201.models.m01_core_mas import User, CustomPermissionModel
from ebos2201.serializers.s01_auth import (
    LoginSerializer,
    LogoutSerializer,
    OtpVerifySerializer,
)


class LoginAPIView(generics.GenericAPIView):
    """
    Getting otp existing users using username or email and password.
    """

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"send": "Two step verification OTP successfully send!!!"},
            status=status.HTTP_200_OK,
        )


class TwoStepVerificationAPIView(generics.GenericAPIView):
    """
    Authenticate existing users using otp.
    """

    serializer_class = OtpVerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            otp = request.data.get("otp")
            user = User.objects.get(otp=otp, is_active=True)
            now = timezone.now()

            if user.otp_expire_at > now:
                user.otp = None
                user.last_login = now
                user.save()

                return Response(
                    self.get_tokens_for_user(user), status=status.HTTP_200_OK
                )
            else:
                raise ExpiredOtpException()

        except User.DoesNotExist:
            raise InvalidOtpException()

    def get_tokens_for_user(self, user: User) -> Dict:
        refresh_token = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
        }


class LogoutView(views.APIView):
    """
    Logout an authenticated user.
    """

    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "The refresh token blacklisted"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


# class AccessContentView(generics.ListAPIView):
#     """
#     List of access permission module of an authenticated user.
#     """

#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = None

#     def get(self, request, format=None):
#         """
#         Return a list of access permission models for the requested user.
#         """
#         contents = {}
#         user = request.user

#         for objs in Permission.objects.filter(
#             Q(user=user) | Q(group__user=user)
#         ).distinct():
#             model_name = objs.content_type.name

#             if contents.__contains__(model_name):
#                 contents[model_name].append(objs.name)
#             else:
#                 contents.update({model_name: [objs.name]})

#         return Response(contents)

class AccessContentView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """
        Return a list of all access permissions models for the requested user.
        """
        contents = {"permissions": []}
        user = request.user

        # Query groups of the user and their associated permissions
        groups = user.groups.all()
        for group in groups:
            for perm in group.permissions.all():
                # Ensure only permissions related to CustomPermissionModel are included
                if perm.content_type.model_class() == CustomPermissionModel:
                    contents["permissions"].append(perm.codename)

        return Response(contents)
