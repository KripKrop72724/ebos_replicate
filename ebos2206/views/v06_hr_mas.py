from typing import Any

from ebos2201.views.api_views.v01_core_mas import MasterGenericViewSet
from ebos2206.models.m06_hr_mas import (
    T06Alw10,
    T06Ded10,
    T06Doc10,
    T06Lon10,
    T06Lvr10,
    T06Tkr10,
)
from ebos2206.serializers.s06_hr_mas import (
    T06Alw10Serializer,
    T06Ded10Serializer,
    T06Doc10Serializer,
    T06Lon10Serializer,
    T06Lvr10Serializer,
    T06Tkr10Serializer,
)


class T06Alw10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing allowance master instances.
    """

    model = T06Alw10
    serializer_class = T06Alw10Serializer


class T06Ded10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing deduction master instances.
    """

    model = T06Ded10
    serializer_class = T06Ded10Serializer


class T06Doc10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing document type instances.
    """

    model = T06Doc10
    serializer_class = T06Doc10Serializer


class T06Lvr10Viewset(MasterGenericViewSet):
    """
    A viewset for viewing and editing leave rules instances.
    """

    model = T06Lvr10
    serializer_class = T06Lvr10Serializer


class T06Lon10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing loan master instances.
    """

    model = T06Lon10
    serializer_class = T06Lon10Serializer


class T06Tkr10ViewSet(MasterGenericViewSet):
    """
    A viewset for viewing and editing Air Ticket Rule instances.
    """

    model = T06Tkr10
    serializer_class = T06Tkr10Serializer
