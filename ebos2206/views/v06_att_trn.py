from django.apps import apps
from django.conf import settings
from django.db.models import ProtectedError
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django_filters.rest_framework import DjangoFilterBackend
from num2words import num2words
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested.viewsets import _force_mutable

from ebos2201.exceptions import (
    LockFlagException,
    PostFlagException,
    ProtectedErrorException,
)
from ebos2201.permissions import IsEmployeeSelfService
from ebos2206.exceptions import NonDeleteLeaveException
from ebos2206.models.m06_att_trn import T06Lve10, T06Prs10, T06Tam10, T06Tbd10, T06Tbm10
from ebos2206.models.m06_prl_trn import T06Prl10, T06Prl11, T06Prl14, T06Prl15, T06Prl16
from ebos2206.serializers.s06_att_trn import (
    T06Ess01Serializer,
    T06Ess05Serializer,
    T06Lve10Serializer,
    T06Prs10LockSerializer,
    T06Prs10Serializer,
    T06Tam10Serializer,
    T06Tbd10Serializer,
    T06Tbm10Serializer,
)
from ebos2206.utils.u06_attendance import AttendanceCSV
from ebos2206.utils.u06_prl_trn import PrintPSlip


class GenericAttTrnViewSet(viewsets.ModelViewSet):
    """
    A viewset for attendence transaction related instances.
    """

    permission_classes = (IsAuthenticated,)

    @property
    def model(self):
        return apps.get_model(
            app_label=str(self.kwargs["app_label"]),
            model_name=str(self.kwargs["model_name"]),
        )

    def get_queryset(self):
        return self.model.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            # If lock_flag is true, cannot delete the object
            if getattr(instance, "lock_flag", None) and instance.lock_flag:
                raise LockFlagException
            elif getattr(instance, "att_lock_flag", None) and (
                instance.att_lock_flag
                or instance.prl_lock_flag
                or instance.prl_post_flag
                or instance.pmt_post_flag
            ):
                raise LockFlagException
            elif getattr(instance, "leave_status", None) and instance.leave_status in [
                "2",
                "3",
            ]:  # Approved & Rejected
                raise LockFlagException
            else:
                self.perform_destroy(instance)
                # Remove attendance data
                if getattr(instance, "att_lock_flag", None):
                    T06Tam10.objects.filter(payroll_period=instance).delete()
                    T06Tbd10.objects.filter(payroll_period=instance).delete()
                    T06Tbm10.objects.filter(payroll_period=instance).delete()

                return Response(status=status.HTTP_204_NO_CONTENT)

        # if protected, cannot be deleted, show error message
        except ProtectedError as exception:
            raise ProtectedErrorException


class T06Prs10ViewSet(GenericAttTrnViewSet):
    """
    A viewset for viewing and editing payroll run setup instances.
    """

    model = T06Prs10
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = T06Prs10Serializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["division", "payroll_group", "pay_year", "pay_month"]

    # Action for `machine_data_lock`
    # Action for `daily_data_lock`
    # Action for `monthly_data_lock`
    @action(
        detail=False,
        methods=["post"],
        serializer_class=T06Prs10LockSerializer,
        parser_classes=[JSONParser],
    )
    def attendance_data_lock(self, request):
        msg = "Something went wrong"
        try:
            posted = 0
            msg = "Attendance data cannot be locked."

            if ids := request.data.get("payroll_run_ids", None):
                for id in ids:
                    obj = T06Prs10.objects.get(pk=id)

                    if obj.att_lock_flag == False:
                        if request.data["prg_type"] == "TAM":
                            T06Tbd10.get_TAM_data(obj)
                            T06Tbm10.read_TBD_log(obj)
                        elif request.data["prg_type"] == "TBD":
                            T06Tbm10.read_TBD_log(obj)

                        obj.att_lock_flag = True
                        obj.save()

                        # Update the attendace data lock
                        T06Tam10.objects.filter(
                            payroll_period=obj, lock_flag=False
                        ).update(lock_flag=True)
                        T06Tbd10.objects.filter(
                            payroll_period=obj, lock_flag=False
                        ).update(lock_flag=True)
                        T06Tbm10.objects.filter(
                            payroll_period=obj, lock_flag=False
                        ).update(lock_flag=True)

                        posted += 1

                        msg = (
                            ngettext(
                                "%s month data successfully locked.",
                                "%s months data successfully locked.",
                                posted,
                            )
                            % num2words(posted).capitalize()
                        )
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        return Response(
                            {"details": "Attendance data already locked."},
                            status=status_code,
                        )
            else:
                msg = "No payroll run setup id found."

            status_code = (
                status.HTTP_200_OK if posted > 0 else status.HTTP_400_BAD_REQUEST
            )
            status_text = True if posted > 0 else False

            return Response({"details": msg}, status=status_code)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"details": msg}, status=status_code)

    # Action for `download machine_data`
    @action(detail=True, methods=["get"])
    def export_machine_attendance(self, request, pk=None):
        file = AttendanceCSV().export_machine_data(pk)
        return Response(
            {"file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file}"},
            status=status.HTTP_200_OK,
        )

    # Action for `download daily_data`
    @action(detail=True, methods=["get"])
    def export_daily_attendance(self, request, pk=None):
        file = AttendanceCSV().export_daily(pk)
        return Response(
            {"file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file}"},
            status=status.HTTP_200_OK,
        )

    # Action for `download monthly_data`
    @action(detail=True, methods=["get"])
    def export_monthly_attendance(self, request, pk=None):
        file = AttendanceCSV().export_monthly(pk)
        return Response(
            {"file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file}"},
            status=status.HTTP_200_OK,
        )

    # Action for `delete attendance data`
    @action(detail=True, methods=["get"])
    def delete_attendance_data(self, request, pk=None):
        try:
            instance = T06Prs10.objects.get(pk=pk)

            # If lock_flag is true, cannot delete the object
            if (
                instance.att_lock_flag
                or instance.prl_lock_flag
                or instance.prl_post_flag
                or instance.pmt_post_flag
            ):
                raise LockFlagException
            else:
                # Remove attendance data
                T06Tam10.objects.filter(payroll_period=instance).delete()
                T06Tbd10.objects.filter(payroll_period=instance).delete()
                T06Tbm10.objects.filter(payroll_period=instance).delete()

                # Remove attendance and daily csv file
                instance.attn_machine_file = None
                instance.daily_attn_file = None
                instance.save()

                return Response(
                    {"details": "All attendance data are removed."},
                    status=status.HTTP_204_NO_CONTENT,
                )
        # if protected, cannot be deleted, show error message
        except ProtectedError:
            raise ProtectedErrorException
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Action for `delete payroll summery data`
    @action(detail=True, methods=["get"])
    def delete_payroll_summery(self, request, pk=None):
        instance = T06Prs10.objects.get(pk=pk)

        try:
            # If prl_post_flag is true, cannot delete the object
            if instance.prl_post_flag:
                raise PostFlagException
            else:
                # Remove T06Prl10 data
                T06Prl10.objects.filter(payroll_period=instance).delete()

                # Update the related flag
                instance.att_lock_flag = False
                instance.prl_lock_flag = False
                instance.prl_run_flag = False
                instance.save()

                # Update the attendace data lock
                T06Tam10.objects.filter(payroll_period=instance, lock_flag=True).update(
                    lock_flag=False
                )
                T06Tbd10.objects.filter(payroll_period=instance, lock_flag=True).update(
                    lock_flag=False
                )
                T06Tbm10.objects.filter(payroll_period=instance, lock_flag=True).update(
                    lock_flag=False
                )

                return Response(
                    {"details": "All payroll data are removed."},
                    status=status.HTTP_204_NO_CONTENT,
                )  # if protected, cannot be deleted, show error message
        except ProtectedError as exception:
            raise ProtectedErrorException

    # Action for `update ticket amount`
    # `update loan EMI amount`
    # `update deduction amount`
    # `update labour cost`
    @action(detail=True, methods=["get"])
    def update_payroll_amount(self, request, pk=None):
        instance = T06Prs10.objects.get(pk=pk)
        if not instance.prl_lock_flag:
            T06Prl14.update_t06prl14(instance)
            T06Prl15.update_t06prl15(instance)
            T06Prl16.update_t06prl16(instance)
            T06Prl11.update_t06prl11(instance)

            # Update T06Prs10 flag
            instance.prl_lock_flag = True
            instance.save()

            return Response(
                {"details": "The payroll amount was successfully updated."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"details": "The payroll process already locked."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GenericAttendanceViewSet(GenericAttTrnViewSet):
    """
    A viewset for attendence related instances.
    """

    def get_queryset(self):
        """
        Filter the `QuerySet` based on its parents as defined in the
        `serializer_class.parent_lookup_kwargs` or `viewset.parent_lookup_kwargs`
        """
        queryset = self.model.objects.all()

        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        orm_filters = {}
        parent_lookup_kwargs = getattr(
            self.get_serializer_class(), "parent_lookup_kwargs", None
        )
        for query_param, field_name in parent_lookup_kwargs.items():
            orm_filters[field_name] = self.kwargs[query_param]
        return queryset.filter(**orm_filters)

    def initialize_request(self, request, *args, **kwargs):
        """
        Adds the parent params from URL inside the children data available
        """
        request = super().initialize_request(request, *args, **kwargs)

        if parent_lookup_kwargs := getattr(
            self.get_serializer_class(), "parent_lookup_kwargs", None
        ):
            for url_kwarg, fk_filter in parent_lookup_kwargs.items():
                # fk_filter is alike 'grandparent__parent__pk'
                parent_arg = fk_filter.partition("__")[0]
                for querydict in [request.data, request.query_params]:
                    with _force_mutable(querydict):
                        querydict[parent_arg] = kwargs.get("url_kwarg", None)
        return request


class T06Tam10ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing time machine data instances.
    """

    model = T06Tam10
    serializer_class = T06Tam10Serializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = [
        "employee_code",
    ]


class T06Tbd10ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing daily attendance data instances.
    """

    model = T06Tbd10
    serializer_class = T06Tbd10Serializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = [
        "employee_code",
    ]


class T06Tbm10ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing monthly attendance data instances.
    """

    model = T06Tbm10
    serializer_class = T06Tbm10Serializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = [
        "employee_code",
    ]


class T06Lve10Viewset(GenericAttTrnViewSet):
    """
    A viewset for viewing and editing leave application data instances.
    """

    model = T06Lve10
    serializer_class = T06Lve10Serializer


class T06Ess01ViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing self service leave application instances.
    """

    permission_classes = (IsEmployeeSelfService,)
    serializer_class = T06Ess01Serializer

    def get_queryset(self):
        return T06Lve10.objects.filter(
            employee_code__employee_code=self.request.user.username
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # If leave status approved or rejected, cannot delete the object
        if getattr(instance, "leave_status", None) and instance.leave_status in [
            "2",
            "3",
        ]:
            raise NonDeleteLeaveException

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class T06Ess05ViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing self payslip instances.
    """

    permission_classes = (IsEmployeeSelfService,)
    serializer_class = T06Ess05Serializer
    http_method_names = ["get"]

    def get_queryset(self):
        prl_obj_list = T06Prl10.objects.filter(
            employee_code__employee_code=self.request.user.username
        ).values("payroll_period_id")
        return T06Prs10.objects.filter(id__in=prl_obj_list)

    @action(detail=True, methods=["get"])
    def download_payslip(self, request, pk=None):
        try:
            PrintPSlip(
                ins=T06Prs10.objects.get(id=pk),
                employee_code=self.request.user.username,
            )
            return Response(
                {
                    "file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}payslips/payslip_{self.request.user.username}.pdf"
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class T06Ess06ViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing self service monthly timesheet instances.
    """

    permission_classes = (IsEmployeeSelfService,)
    serializer_class = T06Tbm10Serializer
    http_method_names = ["get"]

    def get_queryset(self):
        return T06Tbm10.objects.filter(
            employee_code__employee_code=self.request.user.username
        )
