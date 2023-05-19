from decimal import Decimal

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import BasePermission


from ebos2201.serializers.s01_core_mas import DeleteIdsSerializer
from ebos2201.utils import get_path
from ebos2201.views.api_views.v01_core_mas import (
    DivisionRelatedBaseViewSet,
    MasterGenericViewSet,
)
from ebos2210.filters import CustomAllocationDBCRFilter, CustomVoucherFilter, CustomT10Glr02Filter
from ebos2210.models.m10_fin_gl import T10Alc10, T10Alc11, T10Alc12, T10Glr01, T10Glr02
from ebos2210.models.m10_fin_link import T10Gld11
from ebos2210.serializers.s10_fin_gl import (
    T10Alc10CreditSerializer,
    T10Alc10DebitSerializer,
    T10Alc10ReadSerializer,
    T10Alc10WriteSerializer,
    T10Alc11Serializer,
    T10Alc12Serializer,
    T10Glr01Serializer,
    T10Glr02Serializer,
)
from ebos2210.views.v10_gl_alloc import GlAllocRpt, GlAllocRptExl


class CanCreateReports(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_reports" permission
        return request.user.has_perm("ebos2201.create_reports")

class CanReadReports(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_reports" permission
        return request.user.has_perm("ebos2201.read_reports")

class CanUpdateReports(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "update_reports" permission
        return request.user.has_perm("ebos2201.update_reports")

class CanDeleteReports(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "delete_reports" permission
        return request.user.has_perm("ebos2201.delete_reports")

class T10Glr01ViewSet(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing finance reports.
    """

    model = T10Glr01
    serializer_class = T10Glr01Serializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filterset_fields = ("division", "rpt_code", "coa", "subledger")
    ordering_fields = [
        "id",
        "division__division_name",
        "rpt_code",
        "coa__account_name",
        "subledger__subledger_name",
        "dt_from",
        "dt_upto",
    ]
    search_fields = (
        "division__division_name",
        "rpt_code",
        "coa__account_name",
        "subledger__subledger_name",
        "dt_from",
        "dt_upto",
    )

    permission_classes = [CanReadReports]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateReports]
        elif self.action == "update":
            permission_classes = [CanUpdateReports]
        elif self.action == "destroy":
            permission_classes = [CanDeleteReports]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]


class CanCreateFinancialStatement(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_fs" permission
        return request.user.has_perm("ebos2201.create_fs")

class CanReadFinancialStatement(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_fs" permission
        return request.user.has_perm("ebos2201.read_fs")

class CanUpdateFinancialStatement(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "update_fs" permission
        return request.user.has_perm("ebos2201.update_fs")

class CanDeleteFinancialStatement(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "delete_fs" permission
        return request.user.has_perm("ebos2201.delete_fs")

class T10Glr02ViewSet(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing finance statements.
    """

    model = T10Glr02
    serializer_class = T10Glr02Serializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomT10Glr02Filter

    permission_classes = [CanReadFinancialStatement]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateFinancialStatement]
        elif self.action == "update":
            permission_classes = [CanUpdateFinancialStatement]
        elif self.action == "destroy":
            permission_classes = [CanDeleteFinancialStatement]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]


class T10Alc10DBView(generics.GenericAPIView):
    """
    Getting gld11 vouchers for debit allocation.
    """

    serializer_class = T10Alc10DebitSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        division = request.data.get("division")
        coa = request.data.get("coa")
        subledger = request.data.get("subledger")
        date_from = request.data.get("date_from")
        date_to = request.data.get("date_to")

        # Getting Gld11 data
        try:
            T10Alc11_items = []
            # Filter GL Record on the basis of input fields - division and vou_date
            if date_from and date_to:
                debit_allocation_gl_records = T10Gld11.objects.filter(
                    vou_id__division=division,
                    vou_id__delete_flag=False,
                    vou_id__post_flag=True,
                    vou_coa=coa,
                    vou_subledger=subledger,
                    vou_id__vou_date__gte=date_from,
                    vou_id__vou_date__lte=date_to,
                    bcurr_debit__gt=Decimal("0.00"),
                )

                if debit_allocation_gl_records.exists():
                    for debit_record in debit_allocation_gl_records:
                        # Debit Details for inline
                        alloc_amt_tot = debit_record.alloc_amt_tot or 0
                        debit_open = debit_record.bcurr_debit + alloc_amt_tot

                        if debit_open > 0:
                            debit_ref = (
                                debit_record.vou_id.vou_hdr_ref
                                if debit_record.vou_id.vou_hdr_ref
                                else debit_record.vou_line_ref
                            )
                            debit_narration = (
                                debit_record.narration
                                if debit_record.narration
                                else f"{debit_record.vou_id.comment1 or ''} {debit_record.vou_id.comment2 or ''}"
                            )

                            # Create object for T10Alc11
                            T10Alc11_items.append(
                                {
                                    "debit_id": debit_record.id,
                                    "debit_alloc": debit_open,
                                    "debit_ref": debit_ref,
                                    "debit_vou": debit_record.vou_id.vou_num,
                                    "debit_due_dt": debit_record.due_date,
                                    "vou_date": debit_record.vou_id.vou_date,
                                    "narration": debit_narration,
                                    "debit_open": debit_open,
                                }
                            )

                    return Response(
                        {"allocation_db": T10Alc11_items}, status=status.HTTP_200_OK
                    )

                return Response(
                    {"details": "No record found"}, status=status.HTTP_204_NO_CONTENT
                )

        except Exception as e:
            return Response(
                {"details": "Cannot get record"}, status=status.HTTP_404_NOT_FOUND
            )


class T10Alc10CrView(generics.GenericAPIView):
    """
    Getting gld11 vouchers for credit allocation.
    """

    serializer_class = T10Alc10CreditSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        division = request.data.get("division")
        coa = request.data.get("coa")
        subledger = request.data.get("subledger")
        cr_date_from = request.data.get("cr_date_from")
        cr_date_upto = request.data.get("cr_date_upto")

        # Getting Gld11 data
        try:
            T10Alc12_items = []
            # Filter GL Record on the basis of input fields - division and vou_date
            if cr_date_from and cr_date_upto:
                credit_allocation_gl_records = T10Gld11.objects.filter(
                    vou_id__division=division,
                    vou_id__delete_flag=False,
                    vou_id__post_flag=True,
                    vou_coa=coa,
                    vou_subledger=subledger,
                    vou_id__vou_date__gte=cr_date_from,
                    vou_id__vou_date__lte=cr_date_upto,
                    bcurr_credit__gt=Decimal("0.00"),
                )

                if credit_allocation_gl_records.exists():
                    for credit_record in credit_allocation_gl_records:
                        # Credit Details for inline
                        alloc_amt_tot = credit_record.alloc_amt_tot or 0
                        gl_credit_open = credit_record.bcurr_credit - alloc_amt_tot

                        if gl_credit_open > 0:
                            credit_ref = (
                                credit_record.vou_id.vou_hdr_ref
                                if credit_record.vou_id.vou_hdr_ref
                                else credit_record.vou_line_ref
                            )
                            credit_narration = (
                                credit_record.narration
                                if credit_record.narration
                                else f"{credit_record.vou_id.comment1 or ''} {credit_record.vou_id.comment2 or ''}"
                            )

                            # Create object for T10Alc12
                            T10Alc12_items.append(
                                {
                                    "credit_id": credit_record.id,
                                    "credit_alloc": gl_credit_open,
                                    "credit_ref": credit_ref,
                                    "credit_vou": credit_record.vou_id.vou_num,
                                    "credit_due_dt": credit_record.due_date,
                                    "vou_date": credit_record.vou_id.vou_date,
                                    "narration": credit_narration,
                                    "credit_open": gl_credit_open,
                                }
                            )

                    return Response(
                        {"allocation_cr": T10Alc12_items}, status=status.HTTP_200_OK
                    )

                return Response(
                    {"details": "No record found"}, status=status.HTTP_204_NO_CONTENT
                )

        except Exception as e:
            return Response(
                {"details": "Cannot get record"}, status=status.HTTP_404_NOT_FOUND
            )

class CanCreateAllocation(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_allocation" permission
        return request.user.has_perm("ebos2201.create_allocation")

class CanReadAllocation(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_allocation" permission
        return request.user.has_perm("ebos2201.read_allocation")

class CanUpdateAllocation(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "update_allocation" permission
        return request.user.has_perm("ebos2201.update_allocation")

class CanDeleteAllocation(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "delete_allocation" permission
        return request.user.has_perm("ebos2201.delete_allocation")



class T10Alc10Viewset(MasterGenericViewSet):
    """
    A viewset for viewing and editing allocation instances.
    """

    model = T10Alc10
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filterset_class = CustomVoucherFilter
    ordering_fields = [
        "division__division_name",
        "vou_num",
        "vou_date",
        "coa__account_name",
        "subledger__subledger_name",
    ]
    search_fields = (
        "division__division_name",
        "vou_type__voucher_type",
        "vou_num",
        "vou_type__voucher_name__voucher_name",
        "line_narration",
        "coa__account_name",
        "subledger__subledger_name",
        "date_from",
        "date_to",
        "cr_date_from",
        "cr_date_upto",
        "hdr_comment",
        "issued_to",
        "tot_amount",
        "chq_num",
        "chq_date",
    )

    permission_classes = [CanReadAllocation]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateAllocation]
        elif self.action == "update":
            permission_classes = [CanUpdateAllocation]
        elif self.action == "destroy":
            permission_classes = [CanDeleteAllocation]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        self.queryset = (
            self.model.objects.prefetch_related("allocation_db")
            .prefetch_related("allocation_cr")
            .filter(division__user=self.request.user)
        )
        return super(MasterGenericViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T10Alc10WriteSerializer
        elif self.action == "delete_records":
            return DeleteIdsSerializer

        return T10Alc10ReadSerializer

    @action(detail=True, methods=["get"], url_path="print")
    def print_allocation(self, request, pk=None):
        try:
            gl_alloc = T10Alc10.objects.get(pk=pk)
            gl_alloc_rpt = GlAllocRpt()
            gl_alloc_rpt.init_pdf(gl_alloc)

            # passing debit details
            for db_detail in gl_alloc.allocation_db.all():
                gl11_detail = T10Gld11.objects.get(id=db_detail.debit_id)
                gl_alloc_rpt.render_details(db_detail, gl11_detail, "debit")

            # passing credit details
            for cr_detail in gl_alloc.allocation_cr.all():
                gl11_detail = T10Gld11.objects.get(id=cr_detail.credit_id)
                gl_alloc_rpt.render_details(cr_detail, gl11_detail, "credit")

            gl_alloc_rpt.print_pdf(gl_alloc)

            filename = get_path("reports/allocation_report.pdf")

            return Response(
                {
                    "file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{filename}"
                },
                status=status.HTTP_200_OK,
            )
        except T10Gld11.DoesNotExist:
            return Response(
                {"details": "No record found."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"details": e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="download")
    def download_xl_allocation(self, request, pk=None):
        try:
            gl_alloc = T10Alc10.objects.get(pk=pk)
            gl_alloc_rpt = GlAllocRptExl()
            file = gl_alloc_rpt.render_details(gl_alloc)

            filename = get_path("reports/allocation_report.xlsx")

            return Response(
                {"file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{filename}"},
                status=status.HTTP_200_OK,
            )
        except T10Gld11.DoesNotExist:
            return Response(
                {"details": "No record found."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class T10Alc11Viewset(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for listing all allocation debit.
    """

    model = T10Alc11
    permission_classes = (IsAuthenticated,)
    serializer_class = T10Alc11Serializer
    queryset = T10Alc11.objects.all()
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    )
    filterset_class = CustomAllocationDBCRFilter
    search_fields = (
        "alloc_id__division__division_name",
        "alloc_id__vou_type__voucher_type",
        "alloc_id__vou_num",
        "alloc_id__vou_type__voucher_name__voucher_name",
        "narration",
        "alloc_id__coa__account_name",
        "alloc_id__subledger__subledger_name",
        "debit_vou",
        "debit_ref",
        "debit_open",
        "debit_alloc",
        "debit_due_dt",
        "vou_date",
    )
    ordering_fields = [
        "division__division_name",
        "vou_num",
        "vou_date",
        "coa__account_name",
        "subledger__subledger_name",
    ]


class T10Alc12Viewset(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for listing all allocation debit.
    """

    model = T10Alc12
    permission_classes = (IsAuthenticated,)
    serializer_class = T10Alc12Serializer
    queryset = T10Alc12.objects.all()
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = CustomAllocationDBCRFilter
    search_fields = (
        "alloc_id__division__division_name",
        "alloc_id__vou_type__voucher_type",
        "alloc_id__vou_num",
        "alloc_id__vou_type__voucher_name__voucher_name",
        "narration",
        "alloc_id__coa__account_name",
        "alloc_id__subledger__subledger_name",
        "credit_vou",
        "credit_ref",
        "credit_open",
        "credit_alloc",
        "credit_due_dt",
        "vou_date",
    )
