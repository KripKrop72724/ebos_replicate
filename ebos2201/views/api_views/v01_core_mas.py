from typing import Type

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models import Model, ProtectedError, Q
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import filters

from ebos2201.exceptions import ProtectedErrorException
from ebos2201.models.m01_core_mas import (
    T01Atm10,
    T01Cat10,
    T01Com10,
    T01Cur10,
    T01Cur11,
    T01Dep10,
    T01Div10,
    T01Dsg10,
    T01Voc11,
    User,
)
from ebos2201.models.m01_fin_mas import T01Bnk10
from ebos2201.serializers.s01_core_mas import (
    DeleteIdsSerializer,
    GroupSerializer,
    PasswordSerializer,
    PermissionSerializer,
    T01Atm10Serializer,
    T01Bnk10Serializer,
    T01Cat10Serializer,
    T01Com10ReadSerializer,
    T01Com10WriteSerializer,
    T01Cur10Serializer,
    T01Cur11Serializer,
    T01Dep10Serializer,
    T01Div10ReadSerializer,
    T01Div10WriteSerializer,
    T01Dsg10Serializer,
    T01Voc11Serializer,
    UserReadSerializer,
    UserSerializer,
    SimplifiedGroupSerializer
)


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    A viewset for generic model viewset.
    """

    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(
                {"details": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT
            )

        # if protected, cannot be deleted, show error message
        except ProtectedError as exception:
            raise ProtectedErrorException


class MasterGenericViewSet(BaseModelViewSet):
    """
    A generic viewset for viewing and editing master instances.
    """

    model: Type[Model]

    def get_queryset(self):
        return self.model.objects.all()

    @action(
        detail=False,
        methods=["POST"],
        url_path="delete",
        name="Multiple delete",
        serializer_class=DeleteIdsSerializer,
    )
    def delete_records(self, request):
        status_code = status.HTTP_400_BAD_REQUEST
        
        if ids := request.data.get("ids", None):
            try:
                obj = self.get_queryset().filter(id__in=ids).delete()

                # If nothing delete
                if obj[0] < 1:
                    msg = "No record deleted."
                else:
                    msg = "Deleted selected items."
                    status_code = status.HTTP_200_OK

            # if protected, cannot be deleted, show error message
            except ProtectedError as exception:
                raise ProtectedErrorException
        else:
            msg = "No id found."

        return Response({"details": msg}, status=status_code)


class DivisionRelatedBaseViewSet(MasterGenericViewSet):
    """
    A viewset for get queryset depend on division of an authenticate user.
    """

    model: Type[Model]

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("division",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()
            
        try:
            self.queryset = self.model.objects.filter(Q(division__user=self.request.user) | Q(company__in=list(self.request.user.users.values_list("company",flat=True))))
        except:
            self.queryset = self.model.objects.filter(division__user=self.request.user)

        return super(MasterGenericViewSet, self).get_queryset()


class UserViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return UserSerializer
        if self.action in ["set_password"]:
            return PasswordSerializer

        return UserReadSerializer

    @action(detail=True, methods=["put"], name="Change Password")
    def set_password(self, request, pk=None):
        """Update the user's password."""
        user = self.get_object()
        serializer = PasswordSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"status": "Password set"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing and editing Permission instances.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()


# class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     A viewset for viewing and editing Groups instances.
#     """

#     permission_classes = (IsAuthenticated,)
#     serializer_class = GroupSerializer
#     queryset = Group.objects.all()

class GroupsViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, editing, and deleting Group instances.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'permissions__name', 'permissions__codename']

    def list(self, request, *args, **kwargs):
        all_param = request.query_params.get('all', '').lower() == 'true'
        if all_param:
            queryset = self.get_queryset()
            serializer = SimplifiedGroupSerializer(queryset, many=True)
            return Response({"results": serializer.data})  # call .data on the serializer
        return super().list(request, *args, **kwargs)


class T01Atm10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing Setup Auto email instances.
    """

    model = T01Atm10
    serializer_class = T01Atm10Serializer


class T01Com10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing company instances.
    """

    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        qs = T01Com10.objects.all()
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T01Com10WriteSerializer

        return T01Com10ReadSerializer


class T01Cur10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing currency instances.
    """

    serializer_class = T01Cur10Serializer
    queryset = T01Cur10.objects.all()


class T01Cur11ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing currency rate instances.
    """

    serializer_class = T01Cur11Serializer
    queryset = T01Cur11.objects.all()


class T01Bnk10ViewSet(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing and editing bank instances.
    """

    model = T01Bnk10
    serializer_class = T01Bnk10Serializer


class T01Div10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing division instances.
    """

    model = T01Div10

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        return self.model.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T01Div10WriteSerializer

        return T01Div10ReadSerializer


class T01Dep10ViewSet(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing department instances.
    """

    model = T01Dep10
    serializer_class = T01Dep10Serializer


class T01Dsg10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing designation instances.
    """

    model = T01Dsg10
    serializer_class = T01Dsg10Serializer


class T01Cat10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing category instances.
    """

    model = T01Cat10
    serializer_class = T01Cat10Serializer


class T01Voc11ViewSet(BaseModelViewSet):
    """
    A viewset for viewing voucher type instances.
    """

    model = T01Voc11
    serializer_class = T01Voc11Serializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("voucher_name__division", "voucher_name__prg_type")
    http_method_names = ["get"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        qs = self.model.objects.filter(voucher_name__division__user=self.request.user)
        return qs
