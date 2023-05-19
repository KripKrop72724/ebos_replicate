import operator
from functools import reduce

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from ebos2201.models.m01_core_mas import T01Div10
from ebos2201.models.m01_fin_mas import T01Act10, T01Cfl10, T01Coa10, T01Sld10, T01Slt10


class DivisionAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = T01Div10.objects.filter(user=self.request.user)
        if self.q:
            qs = qs.filter(division_name__icontains=self.q)
        return qs


class ParentAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def __init__(self, model, field, forward, search_arg, filter_kwargs):
        self.model = model
        self.field = field
        self.forward = forward
        self.filter_kwargs = filter_kwargs
        self.search_arg = search_arg

    def get_queryset(self):
        forward_id = self.forwarded.get(self.forward, None)

        if not forward_id:
            return self.model.objects.none()

        self.filter_kwargs.update({f"{self.field}": forward_id})
        qs = self.model.objects.filter(**self.filter_kwargs)
        if self.q:
            list_of_Q = [
                Q(**{f"{search}__icontains": self.q}) for search in self.search_arg
            ]
            qs = qs.filter(reduce(operator.or_, list_of_Q))
        return qs


class ParentCoaAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        filter_kwargs = {"coa_control": "1"}
        search_arg = ["account_name", "account_num"]
        super(ParentAutocomplete, self).__init__(
            model=T01Coa10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class ActivityGroupAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        filter_kwargs = {}
        search_arg = ["activity_name"]
        super(ParentAutocomplete, self).__init__(
            model=T01Act10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class CashflowGroupAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        filter_kwargs = {}
        search_arg = ["cashflow_desc"]
        super(ParentAutocomplete, self).__init__(
            model=T01Cfl10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class SubledgerTypeAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        filter_kwargs = {}
        search_arg = ["sl_type_desc", "sl_type_code"]
        super(ParentAutocomplete, self).__init__(
            model=T01Slt10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class SldAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        filter_kwargs = {}
        search_arg = ["subledger_name", "subledger_code"]

        super(ParentAutocomplete, self).__init__(
            model=T01Sld10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )
