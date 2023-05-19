from ebos2206.models.m06_prl_trn import (
    T06Prl10,
    T06Prl11,
    T06Prl12,
    T06Prl13,
    T06Prl14,
    T06Prl15,
    T06Prl16,
)
from ebos2206.serializers.s06_prl_trn import (
    T06Prl10Serializer,
    T06Prl11Serializer,
    T06Prl12Serializer,
    T06Prl13Serializer,
    T06Prl14Serializer,
    T06Prl15Serializer,
    T06Prl16Serializer,
)

from .v06_att_trn import GenericAttendanceViewSet


class T06Prl10ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll summery instances.
    """

    model = T06Prl10
    serializer_class = T06Prl10Serializer
    http_method_names = ["get"]


class T06Prl11ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll labour cost instances.
    """

    model = T06Prl11
    serializer_class = T06Prl11Serializer
    http_method_names = ["get"]


class T06Prl12ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll leave amount instances.
    """

    model = T06Prl12
    serializer_class = T06Prl12Serializer
    http_method_names = ["get"]


class T06Prl13ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll allowance amount instances.
    """

    model = T06Prl13
    serializer_class = T06Prl13Serializer
    http_method_names = ["get"]


class T06Prl14ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll ticket amount instances.
    """

    model = T06Prl14
    serializer_class = T06Prl14Serializer
    http_method_names = ["get", "patch"]


class T06Prl15ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll loan emi instances.
    """

    model = T06Prl15
    serializer_class = T06Prl15Serializer
    http_method_names = ["get", "patch"]


class T06Prl16ViewSet(GenericAttendanceViewSet):
    """
    A viewset for viewing and editing payroll deduction amount instances.
    """

    model = T06Prl16
    serializer_class = T06Prl16Serializer
    http_method_names = ["get", "patch"]
