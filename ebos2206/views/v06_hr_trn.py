from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from ebos2201.permissions import IsEmployeeSelfService
from ebos2201.views.api_views.v01_core_mas import BaseModelViewSet
from ebos2206.models.m06_hr_trn import T06Eos10, T06Exc10, T06Hdt10, T06Mem10, T06Wps10
from ebos2206.serializers.s06_hr_trn import (
    T06Eos10Serializer,
    T06Ess02Serializer,
    T06Ess03Serializer,
    T06Exc10Serializer,
    T06Hdt10Serializer,
    T06Mem10Serializer,
    T06Wps10Serializer,
)
from ebos2206.utils.u06_hr_trn import EOSExport, WPSExport


class T06Wps10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing wps sif files instances.
    """

    model = T06Wps10
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = T06Wps10Serializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        qs = self.model.objects.prefetch_related("wps_header_set").filter(
            division__user=self.request.user
        )
        return qs

    @action(detail=True, methods=["get"])
    def export_wps_csv(self, request, pk=None):
        file = WPSExport().wps_csv_data(self.model.objects.get(id=pk))
        return Response(
            {"file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file}"},
            status=status.HTTP_200_OK,
        )


class T06Eos10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing end of service instances.
    """

    model = T06Eos10
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = T06Eos10Serializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        qs = self.model.objects.all()
        return qs

    @action(detail=True, methods=["get"])
    def export_eos_pdf(self, request, pk=None):
        file = EOSExport().eos_pdf_data(self.model.objects.get(id=pk))
        return Response(
            {"file_path": f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file}"},
            status=status.HTTP_200_OK,
        )


class T06Mem10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing employee memo instances.
    """

    model = T06Mem10
    serializer_class = T06Mem10Serializer
    queryset = model.objects.all()


class T06Exc10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing employee expanse claim instances.
    """

    model = T06Exc10
    serializer_class = T06Exc10Serializer
    queryset = model.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # If claim_status paid or rejected, cannot delete the object
        if getattr(instance, "claim_status", None) and instance.claim_status in [
            "3",
            "4",
        ]:
            return Response(
                {"detail": "This claim cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class T06Hdt10ViewSet(BaseModelViewSet):
    """
    A viewset for viewing and editing help desk ticket instances.
    """

    model = T06Hdt10
    serializer_class = T06Hdt10Serializer
    queryset = model.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # If service_status proccesing, closed, cannot delete the object
        if getattr(instance, "service_status", None) and instance.service_status == "3":
            return Response(
                {"detail": "This ticket cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Employe self services
class T06Ess02ViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing self service expanse claim instances.
    """

    permission_classes = (IsEmployeeSelfService,)
    serializer_class = T06Ess02Serializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return T06Exc10.objects.filter(
            employee_code__employee_code=self.request.user.username
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # If claim_status proccesing, paid or rejected, cannot delete the object
        if getattr(instance, "claim_status", None) and instance.claim_status in [
            "2",
            "3",
            "4",
        ]:
            return Response(
                {"detail": "This claim cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class T06Ess03ViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing self service help desk instances.
    """

    permission_classes = (IsEmployeeSelfService,)
    serializer_class = T06Ess03Serializer

    def get_queryset(self):
        return T06Hdt10.objects.filter(
            employee_code__employee_code=self.request.user.username
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # If service_status proccesing, closed, cannot delete the object
        if getattr(instance, "service_status", None) and instance.service_status in [
            "2",
            "3",
        ]:
            return Response(
                {"detail": "This ticket cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class T06Ess04ViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing self service memo instances.
    """

    permission_classes = (IsEmployeeSelfService,)
    serializer_class = T06Mem10Serializer
    http_method_names = ["get"]

    def get_queryset(self):
        return T06Mem10.objects.filter(
            employee_code__employee_code=self.request.user.username
        )
