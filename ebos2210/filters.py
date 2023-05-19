# from django_filters import FilterSet, AllValuesFilter
from typing import Type

from django.db.models import Model
from django_filters import rest_framework as filters

from ebos2201.models.m01_core_mas import T01Com10, T01Div10, T01Voc11


class MultiValueCharFilter(filters.BaseCSVFilter, filters.CharFilter):
    def filter(self, qs, value):
        # value is either a list or an 'empty' value
        qs = super(MultiValueCharFilter, self).filter(qs, value)

        return qs


class CustomVoucherFilter(filters.FilterSet):
    """
    A Custom Filterset for filtering vou_date range, division, vou_num and vou_type.
    """

    model: Type[Model]

    from_vou_date = filters.DateFilter(field_name="vou_date", lookup_expr="gte")
    to_vou_date = filters.DateFilter(field_name="vou_date", lookup_expr="lte")
    division = filters.ModelChoiceFilter(
        field_name="division", queryset=T01Div10.objects.all()
    )
    vou_num = filters.NumberFilter(field_name="vou_num", lookup_expr="exact")
    vou_type = filters.ModelChoiceFilter(
        field_name="vou_type", queryset=T01Voc11.objects.all()
    )
    prg_type__in = MultiValueCharFilter(
        field_name="vou_type__voucher_name__prg_type", label="Prg Type", lookup_expr='in'
    )

    class Meta:
        fields = ["from_vou_date", "to_vou_date", "division", "vou_num", "vou_type", "prg_type__in"]


class CustomAllocationDBCRFilter(filters.FilterSet):
    """
    A Custom Filterset for filtering vou_date range, parent allocation.
    """

    model: Type[Model]

    from_vou_date = filters.DateFilter(field_name="vou_date", lookup_expr="gte")
    to_vou_date = filters.DateFilter(field_name="vou_date", lookup_expr="lte")

    class Meta:
        fields = [
            "from_vou_date",
            "to_vou_date",
            "allocation",
        ]


class CustomT10Glr02Filter(filters.FilterSet):
    """
    A Custom Filterset for filtering rpt code.
    """

    model: Type[Model]

    company = filters.ModelChoiceFilter(
        field_name="company", queryset=T01Com10.objects.all()
    )
    division = filters.ModelChoiceFilter(
        field_name="division", queryset=T01Div10.objects.all()
    )
    rpt_code = MultiValueCharFilter(
        field_name="rpt_code", label="Rpt Code", lookup_expr='in'
    )
    year = filters.NumberFilter(field_name="year", lookup_expr="exact")
    period = filters.NumberFilter(field_name="month", lookup_expr="exact")

    class Meta:
        fields = [
            "company", 
            "division", 
            "rpt_code",
            "year", 
            "period"
        ]
