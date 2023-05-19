from typing import Any

from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter

from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.permissions import BasePermission
from django.http import HttpResponse

from ebos2201.models.m01_fin_mas import (
    T01Act10,
    T01Cfl10,
    T01Coa10,
    T01Prj10,
    T01Sld10,
    T01Slt10,
)
from ebos2201.serializers.s01_core_mas import DeleteIdsSerializer
from ebos2201.serializers.s01_fin_mas import (
    T01Act10Serializer,
    T01Cfl10Serializer,
    T01Coa10ReadSerializer,
    T01Coa10WriteSerializer,
    T01Prj10Serializer,
    T01Sld10ReadSerializer,
    T01Sld10writeSerializer,
    T01Slt10Serializer,
)
from ebos2201.views.api_views.v01_core_mas import (
    BaseModelViewSet,
    DivisionRelatedBaseViewSet,
    MasterGenericViewSet,
)


class CanReadCOA(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_coa" permission
        return request.user.has_perm("ebos2201.read_coa")

class CanUpdateCOA(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "update_coa" permission
        return request.user.has_perm("ebos2201.update_coa")

class CanDeleteCOA(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "delete_coa" permission
        return request.user.has_perm("ebos2201.delete_coa")

class CanCreateCOA(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_coa" permission
        return request.user.has_perm("ebos2201.create_coa")

class T01Coa10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing Chart of account instances.
    """
    model = T01Coa10
    filter_backends = (SearchFilter, filters.DjangoFilterBackend, OrderingFilter)
    filterset_fields = (
        "division",
        "coa_control",
        "account_type",
        "account_group",
        "coa_sl_cat",
        "coa_sl_type",
    )
    ordering_fields = [
        "id",
        "account_num",
        "parent__account_name",
        "account_name",
        "coa_control",
        "account_type",
        "coa_sl_cat",
        "account_group",
    ]
    search_fields = (
        "id",
        "account_num",
        "parent__account_name",
        "account_name",
        "coa_control",
        "account_type",
        "coa_sl_cat",
        "account_group",
    )

    permission_classes = [CanReadCOA]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateCOA]
        elif self.action == "update":
            permission_classes = [CanUpdateCOA]
        elif self.action == "destroy":
            permission_classes = [CanDeleteCOA]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        self.queryset = self.model.objects.filter(
            division__user=self.request.user
        ).order_by("account_group")
        return super(MasterGenericViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T01Coa10WriteSerializer
        elif self.action == "delete_records":
            return DeleteIdsSerializer

        return T01Coa10ReadSerializer

class CanCreateSubledger(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_subledger" permission
        return request.user.has_perm("ebos2201.create_subledger")

class CanReadSubledger(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_subledger" permission
        return request.user.has_perm("ebos2201.read_subledger")

class CanUpdateSubledger(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "update_subledger" permission
        return request.user.has_perm("ebos2201.update_subledger")

class CanDeleteSubledger(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "delete_subledger" permission
        return request.user.has_perm("ebos2201.delete_subledger")


class T01Slt10Viewset(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing and editing SubLedger Type instances.
    """

    model = T01Slt10
    serializer_class = T01Slt10Serializer

    permission_classes = [CanReadSubledger]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateSubledger]
        elif self.action == "update":
            permission_classes = [CanUpdateSubledger]
        elif self.action == "destroy":
            permission_classes = [CanDeleteSubledger]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]


class T01Act10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing Activity Setup instances.
    """

    model = T01Act10
    serializer_class = T01Act10Serializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        return self.model.objects.filter(division__user=self.request.user)


class T01Cfl10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing Cashflow Setup instances.
    """

    model = T01Cfl10
    serializer_class = T01Cfl10Serializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        return self.model.objects.filter(division__user=self.request.user)


class T01Sld10Viewset(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing and editing SubLedger master instances.
    """

    model = T01Sld10
    filter_backends = (SearchFilter, filters.DjangoFilterBackend, OrderingFilter)
    filterset_fields = (
        "division",
        "proxy_code",
        "subledger_type",
        "subledger_cat",
    )
    ordering_fields = [
        "division__division_name",
        "subledger_name",
        "subledger_code",
        "subledger_cat",
    ]
    search_fields = (
        "division__division_name",
        "subledger_name",
        "subledger_code",
        "subledger_cat",
    )

    permission_classes = [CanReadSubledger]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateSubledger]
        elif self.action == "update":
            permission_classes = [CanUpdateSubledger]
        elif self.action == "destroy":
            permission_classes = [CanDeleteSubledger]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T01Sld10writeSerializer

        return T01Sld10ReadSerializer


class T01Prj10ViewSet(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing department instances.
    """

    model = T01Prj10
    serializer_class = T01Prj10Serializer
    http_method_names = ["get"]
