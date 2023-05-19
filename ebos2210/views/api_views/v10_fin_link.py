from django.conf import settings
from django.utils.translation import ngettext
from django_filters.rest_framework import DjangoFilterBackend
from num2words import num2words
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from ebos2201.serializers.s01_core_mas import DeleteIdsSerializer
from ebos2201.views.api_views.v01_core_mas import (
    BaseModelViewSet,
    DivisionRelatedBaseViewSet,
)
from ebos2210.filters import CustomVoucherFilter
from ebos2210.models.m10_fin_link import T10Gld10, T10Tax10, T10Wor10
from ebos2210.serializers.s10_fin_link import (
    T10Gld10IdsSerializer,
    T10Gld10ReadSerializer,
    T10Gld10Serializer,
    T10Tax10Serializer,
    T10Wor10ReadSerializer,
    T10Wor10WriteSerializer,
)
from ebos2210.utils.u10_action_handler import gl_voucher_print

from rest_framework.permissions import BasePermission



class T10Wor10Viewset(DivisionRelatedBaseViewSet):
    """
    A viewset for viewing and editing work order instances.
    """

    model = T10Wor10

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T10Wor10WriteSerializer
        elif self.action == "delete_records":
            return DeleteIdsSerializer

        return T10Wor10ReadSerializer


class T10Tax10ViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing tax setup instances.
    """

    serializer_class = T10Tax10Serializer
    queryset = T10Tax10.objects.all()


class CanCreateGeneralVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.create_jv")

class CanReadGeneralVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.read_jv")

class CanUpdateGeneralVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.update_jv")

class CanDeleteGeneralVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.delete_jv")

class CanPostGeneralVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.post_jv")

class CanCreatePaymentVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.create_pv")

class CanReadPaymentVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.read_pv")

class CanUpdatePaymentVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.update_pv")

class CanDeletePaymentVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.delete_pv")

class CanPostPaymentVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.post_pv")

class CanCreateReceiptVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.create_rv")

class CanReadReceiptVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.read_rv")

class CanUpdateReceiptVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.update_rv")

class CancellationnDeleteReceiptVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.delete_rv")

class CanPostReceiptVoucher(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.post_rv")

class CanCreateDebitNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.create_dn")

class CanReadDebitNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.read_dn")

class CanUpdateDebitNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.update_dn")

class CancellationnDeleteDebitNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.delete_dn")

class CanPostDebitNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.post_dn")

class CanUnPostDebitNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.unpost_dn")

class CanCreateCreditNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.create_cn")

class CanReadCreditNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.read_cn")

class CanUpdateCreditNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.update_cn")

class CancellationnDeleteCreditNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "read_jv" permission
        return request.user.has_perm("ebos2201.delete_cn")

class CanPostCreditNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.post_cn")

class CanUnPostCreditNote(BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the "create_jv" permission
        return request.user.has_perm("ebos2201.unpost_cn")


class T10Gld10Viewset(BaseModelViewSet):
    """
    A viewset for viewing and editing voucher instances.

    """
    model = T10Gld10
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filterset_class = CustomVoucherFilter
    ordering_fields = [
        "division__division_name",
        "vou_num",
        "vou_date",
        "comment1",
        "total_amount",
        "post_flag",
    ]
    search_fields = [
        "division__division_name",
        "vou_num",
        "vou_type__voucher_type",
        "vou_type__voucher_name__voucher_name",
        "vou_date",
        "total_amount",
        "subledger__subledger_name",
        "comment1",
    ]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        qs = (
            self.model.objects.prefetch_related("gld_header_set")
            .prefetch_related("gld12_details_set")
            .filter(division__user=self.request.user)
        )

        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return T10Gld10Serializer
        elif self.action in ["post_voucher", "unpost_voucher", "delete_records"]:
            return T10Gld10IdsSerializer

        return T10Gld10ReadSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.post_flag == False:
            self.perform_destroy(instance)
            return Response(
                {"details": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"details": "Posted voucher cannot delete."},
                status=status.HTTP_423_LOCKED,
            )

    @action(detail=True, methods=["get"], url_path="print")
    def print_voucher(self, request, pk=None):
        try:
            file_path, new_tab = gl_voucher_print(T10Gld10.objects.get(pk=pk))
            return Response(
                {"file_path": file_path, "new_tab": new_tab}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="post")
    def post_voucher(self, request):
        from django.db.models import Sum

        msg = "Something went wrong"
        try:
            posted = 0
            msg = "Voucher cannot be posted"
            total_balance_equal = True

            if ids := request.data.get("voucher_ids", None):

                # While posting the voucher, check all selected vouchers total debit=total credit, if delete_flag=False, post_flag=False
                gld10_obj = T10Gld10.objects.filter(pk__in=ids, delete_flag=False)
                total_balance = gld10_obj.aggregate(
                    bcurr_debit_total=Sum("gld_header_set__bcurr_debit"), 
                    bcurr_credit_total=Sum("gld_header_set__bcurr_credit"),
                    fcurr_debit_total=Sum("gld_header_set__fcurr_debit"),
                    fcurr_credit_total=Sum("gld_header_set__fcurr_credit"),
                )

                if total_balance:
                    if total_balance["bcurr_debit_total"] != total_balance["bcurr_credit_total"] and total_balance["fcurr_debit_total"] != total_balance["fcurr_credit_total"]:
                        # raise ValueError("Voucher cannot be posted. The vouchers debit credit are not equal.")
                        msg = "Voucher cannot be posted. The vouchers debit credit are not equal."
                        total_balance_equal = False

                if total_balance_equal:
                    for qs in gld10_obj:
                        if qs.post_flag == False:
                            T10Gld10.post_voucher(
                                voc_num=qs.vou_num,
                                voc_type=qs.vou_type,
                                vou_date=qs.vou_date,
                            )
                            posted += 1

                            msg = ngettext(
                                "%s voucher was successfully posted.",
                                "%s vouchers were successfully posted.",
                                posted,
                            ) % num2words(posted)
                        else:
                            status_code = status.HTTP_400_BAD_REQUEST
                            return Response(
                                {"details": "Voucher already posted."}, status=status_code
                            )

            else:
                msg = "No voucher id found."

            status_code = (
                status.HTTP_200_OK if posted > 0 else status.HTTP_400_BAD_REQUEST
            )
            status_text = True if posted > 0 else False

            return Response({"details": msg}, status=status_code)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"details": msg}, status=status_code)

    @action(detail=False, methods=["post"], url_path="unpost")
    def unpost_voucher(self, request):
        msg = "Something went wrong"
        try:
            unposted = 0
            msg = "Voucher cannot be unposted"

            if ids := request.data.get("voucher_ids", None):
                for id in ids:
                    qs = T10Gld10.objects.get(pk=id)
                    if qs.post_flag == True:
                        T10Gld10.unpost_voucher(
                            voc_num=qs.vou_num,
                            voc_type=qs.vou_type,
                            vou_date=qs.vou_date,
                        )
                        unposted += 1

                        msg = ngettext(
                            "%s voucher was successfully unposted.",
                            "%s vouchers were successfully unposted.",
                            unposted,
                        ) % num2words(unposted)
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        return Response(
                            {"details": "Voucher already unposted."}, status=status_code
                        )

            else:
                msg = "No voucher id found."

            status_code = (
                status.HTTP_200_OK if unposted > 0 else status.HTTP_400_BAD_REQUEST
            )
            status_text = True if unposted > 0 else False

            return Response({"details": msg}, status=status_code)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"details": msg}, status=status_code)

    @action(detail=True, methods=["get"])
    def cheque_print(self, request, pk=None):
        from ebos2210.views.v10_cheque_layout_print import CHQLayout

        try:
            obj = T10Gld10.objects.get(pk=pk)

            if obj.vou_type.voucher_name.prg_type != "BPV":
                return Response(
                    {"details": "Only bank voucher allow to print cheque."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            file_path = CHQLayout.init_pdf(request, obj, flag=True)

            if file_path:
                file_url = settings.SITE_DOMAIN + settings.MEDIA_URL + file_path
            else:
                file_url = None

            return Response({"file_path": file_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def cancel_cheque(self, request, pk=None):
        from ebos2210.views.v10_cheque_layout_print import CHQLayout

        try:
            cheque = CHQLayout.cancel_pdf(request, T10Gld10.objects.get(pk=pk))
            if cheque:
                return Response(
                    {"details": "Cheque Cancellation completed."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"details": "Cheque can not cancel."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], url_path="delete", name="Multiple delete")
    def delete_records(self, request):
        status_code = status.HTTP_400_BAD_REQUEST

        if ids := request.data.get("voucher_ids", None):
            delete_vouchers = T10Gld10.objects.filter(id__in=ids)
            if delete_vouchers.filter(post_flag=True):
                msg = "Posted vouchers cannot delete."
            else:
                obj = delete_vouchers.delete()
                
                # If nothing delete
                if obj[0] < 1:
                    msg = "No voucher deleted"
                else:
                    msg = "Deleted selected vouchers"
                    status_code = status.HTTP_200_OK
        else:
            msg = "No voucher id found."

        return Response({"details": msg}, status=status_code)
