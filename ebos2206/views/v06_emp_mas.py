from django.apps import apps
from django.db.models import ProtectedError
from rest_framework_nested.viewsets import _force_mutable
from drf_nested_field_multipart import NestedMultipartParser
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from ebos2201.exceptions import ProtectedErrorException
from ebos2201.views.api_views.v01_core_mas import BaseModelViewSet
from ebos2206.models.m06_emp_mas import (
    T06Dex10,
    T06Emp10,
    T06Emp11,
    T06Emp12,
    T06Emp13,
    T06Emp14,
    T06Emp15,
    T06Emp16,
    T06Emp17,
    T06Emp18,
)
from ebos2206.serializers.s06_emp_mas import (
    T06Dex10Serializer,
    T06Emp10Serializer,
    T06Emp11CreateSerializer,
    T06Emp11Serializer,
    T06Emp12CreateSerializer,
    T06Emp12Serializer,
    T06Emp13CreateSerializer,
    T06Emp13Serializer,
    T06Emp14CreateSerializer,
    T06Emp14Serializer,
    T06Emp15CreateSerializer,
    T06Emp15Serializer,
    T06Emp16CreateSerializer,
    T06Emp16Serializer,
    T06Emp17CreateSerializer,
    T06Emp17Serializer,
    T06Emp18CreateSerializer,
    T06Emp18Serializer,
    EmployeeGenericSerializer,
)


class T06Emp10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing employees instances.
    """

    parser_classes = (MultiPartParser, FormParser)
    queryset = T06Emp10.objects.all()

    def get_serializer_class(self):
        if self.action == "bank_accounts":
            return T06Emp11CreateSerializer
        elif self.action == "leave_records":
            return T06Emp12CreateSerializer
        elif self.action == "allowance_records":
            return T06Emp13CreateSerializer
        elif self.action == "ticket_records":
            return T06Emp14CreateSerializer
        elif self.action == "loan_records":
            return T06Emp15CreateSerializer
        elif self.action == "deduction_records":
            return T06Emp16CreateSerializer
        elif self.action == "asset_records":
            return T06Emp17CreateSerializer
        elif self.action == "document_records":
            return T06Emp18CreateSerializer
        else:
            return T06Emp10Serializer

    def _get_child_data(self, child_model, child_serializer):
        """
        List of data of employee child models
        """
        instance = self.get_object()
        queryset = child_model.objects.filter(employee_code=instance)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = child_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = child_serializer(queryset, many=True)

        return Response(serializer.data)

    def _post_child_data(self, instance, child_model, data_set, delete_set):
        """
        Insert or update the employee child models
        """
        for emp_child in data_set:
            # Replace the instance key
            if "allowance_code" in emp_child.keys():
                emp_child["allowance_code_id"] = emp_child.pop("allowance_code")
            elif "ticket_rule" in emp_child.keys():
                emp_child["ticket_rule_id"] = emp_child.pop("ticket_rule")
            elif "loan_type" in emp_child.keys():
                emp_child["loan_type_id"] = emp_child.pop("loan_type")
            elif "deduction_code" in emp_child.keys():
                emp_child["deduction_code_id"] = emp_child.pop("deduction_code")
            elif "document_name" in emp_child.keys():
                emp_child["document_name_id"] = emp_child.pop("document_name")

            if "id" in emp_child.keys():
                emp_child_obj = child_model.objects.filter(id=emp_child["id"])
                if emp_child_obj.exists():
                    emp_child_obj.update(**emp_child)
                else:
                    continue
            else:
                child_model.objects.create(**emp_child, employee_code=instance)

        # delete records
        try:
            if child_model._meta.object_name == "T06Emp11":
                instance.bank_acct_set.filter(id__in=delete_set).delete()
            elif child_model._meta.object_name == "T06Emp13":
                instance.emp_allow_set.filter(id__in=delete_set).delete()
            elif child_model._meta.object_name == "T06Emp14":
                instance.emp_tic_set.filter(id__in=delete_set).delete()
            elif child_model._meta.object_name == "T06Emp15":
                instance.emp_loan_set.filter(id__in=delete_set).delete()
            elif child_model._meta.object_name == "T06Emp16":
                instance.emp_deduc_set.filter(id__in=delete_set).delete()
            elif child_model._meta.object_name == "T06Emp17":
                instance.emp_ass_set.filter(id__in=delete_set).delete()
            elif child_model._meta.object_name == "T06Emp18":
                instance.emp_doc_set.filter(id__in=delete_set).delete()
        # if protected, cannot be deleted, show error message
        except ProtectedError as exception:
            raise ProtectedErrorException

        return True

    # action for multiple insertion of bank account
    @action(detail=True, methods=["get", "post"], parser_classes=[JSONParser])
    def bank_accounts(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp11,
                child_serializer=T06Emp11Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp11CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp11,
                data_set=request.data.pop("bank_acct_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)

    # action for multiple insertion of leave_records
    @action(detail=True, methods=["get"], parser_classes=[JSONParser])
    def leave_records(self, request, pk=None):
        return self._get_child_data(
            child_model=T06Emp12,
            child_serializer=T06Emp12Serializer,
        )

    @action(detail=True, methods=["get", "post"], parser_classes=[JSONParser])
    def allowance_records(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp13,
                child_serializer=T06Emp13Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp13CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp13,
                data_set=request.data.pop("emp_allow_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], parser_classes=[JSONParser])
    def ticket_records(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp14,
                child_serializer=T06Emp14Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp14CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp14,
                data_set=request.data.pop("emp_tic_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], parser_classes=[JSONParser])
    def loan_records(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp15,
                child_serializer=T06Emp15Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp15CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp15,
                data_set=request.data.pop("emp_loan_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], parser_classes=[JSONParser])
    def deduction_records(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp16,
                child_serializer=T06Emp16Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp16CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp16,
                data_set=request.data.pop("emp_deduc_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], parser_classes=[JSONParser])
    def asset_records(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp17,
                child_serializer=T06Emp17Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp17CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp17,
                data_set=request.data.pop("emp_ass_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)

    @action(
        detail=True, methods=["get", "post"], parser_classes=[NestedMultipartParser]
    )
    def document_records(self, request, pk=None):
        if request.method == "GET":
            return self._get_child_data(
                child_model=T06Emp18,
                child_serializer=T06Emp18Serializer,
            )
        else:
            instance = self.get_object()
            serializer = T06Emp18CreateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)

            self._post_child_data(
                instance=instance,
                child_model=T06Emp18,
                data_set=request.data.pop("emp_doc_set"),
                delete_set=request.data.pop("delete_ids"),
            )

            return Response(serializer.data)


class T06Dex10Viewset(BaseModelViewSet):
    """
    A viewset for viewing and editing document expiry reports instances.
    """

    queryset = T06Dex10.objects.all()
    serializer_class = T06Dex10Serializer


# Single insertion of employee child models

class EmployeeGenericViewSet(BaseModelViewSet):
    """
    A generic viewset for viewing and editing employees all related instances.
    """

    @property
    def model(self):
        return apps.get_model(
            app_label=str(self.kwargs["app_label"]),
            model_name=str(self.kwargs["model_name"]),
        )
    
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


class T06Emp11ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees bank instances.
    """
    model = T06Emp11
    serializer_class = T06Emp11Serializer


class T06Emp12ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Leave Record instances.
    """
    model = T06Emp12    
    serializer_class = T06Emp12Serializer
    http_method_names = ['get']


class T06Emp13ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Allowance Record instances.
    """
    model = T06Emp13
    serializer_class = T06Emp13Serializer


class T06Emp14ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Ticket Record instances.
    """
    model = T06Emp14
    serializer_class = T06Emp14Serializer


class T06Emp15ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Loan Record instances.
    """
    model = T06Emp15
    serializer_class = T06Emp15Serializer


class T06Emp16ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Deductions Record instances.
    """
    model = T06Emp16
    serializer_class = T06Emp16Serializer


class T06Emp17ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Asset Record instances.
    """
    model = T06Emp17
    serializer_class = T06Emp17Serializer


class T06Emp18ViewSet(EmployeeGenericViewSet):
    """
    A viewset for viewing and editing employees Documents Record instances.
    """
    model = T06Emp18
    serializer_class = T06Emp18Serializer
