from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from ebos2201.models.m01_core_mas import T01Voc11
from ebos2201.models.m01_fin_mas import T01Coa10, T01Sld10
from ebos2201.views.v01_autocomplete import ParentAutocomplete


class VouIdAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        from ebos2210.models.m10_fin_link import T10Gld10

        filter_kwargs = {
            "post_flag": True,
            "vou_type__voucher_name__prg_type__in": ["BPV", "CPV"],
        }
        search_arg = ["vou_type__voucher_name__voucher_name", "vou_type__voucher_type"]
        super(ParentAutocomplete, self).__init__(
            model=T10Gld10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class PrePayCoaAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        from ebos2210.models.m10_fin_link import T10Gld11

        filter_kwargs = {}
        search_arg = ["vou_coa__account_name"]
        super(ParentAutocomplete, self).__init__(
            model=T10Gld11,
            field="vou_id_id",
            forward="voucher_id",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class PostableCoaAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        filter_kwargs = {"coa_control": 2}
        search_arg = ["account_name", "account_num"]

        super(ParentAutocomplete, self).__init__(
            model=T01Coa10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class VouTypeAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        division_id = self.forwarded.get("division", None)
        if not division_id:
            return T01Voc11.objects.none()

        # division >> vou_type
        qs = T01Voc11.objects.filter(voucher_name__division_id=division_id)
        if self.forwarded.get("prg_type", None):
            qs = qs.filter(voucher_name__prg_type=self.forwarded["prg_type"])

        if self.q:
            qs = qs.filter(
                Q(voucher_type__icontains=self.q)
                | Q(voucher_name__voucher_name__icontains=self.q)
            )
        return qs


class GlVouCoaAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        vou_type_id = self.forwarded["vou_type_id"]

        if not vou_type_id:
            return T01Coa10.objects.none()

        vou_type_obj = T01Voc11.objects.get(id=vou_type_id).voucher_name
        sl_type = vou_type_obj.subledger_type
        sl_cat = vou_type_obj.subledger_cat

        # vou_type >> vou_coa
        qs = T01Coa10.objects.filter(division=vou_type_obj.division).exclude(
            coa_control=1
        )

        if sl_cat:
            qs = qs.filter(coa_sl_cat=sl_cat)
        if sl_type:
            qs = qs.filter(coa_sl_type=sl_type)

        if self.q:
            qs = qs.filter(
                Q(account_name__icontains=self.q) | Q(account_num__icontains=self.q)
            )

        return qs


class GlVouSubledgerAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        coa_id = self.forwarded["vou_coa"]

        if not coa_id:
            return T01Sld10.objects.none()

        t01coa10_obj = T01Coa10.objects.get(id=coa_id)
        subledger_type = t01coa10_obj.coa_sl_type
        subledger_cat = t01coa10_obj.coa_sl_cat
        if subledger_type is None and subledger_cat is None:
            return T01Sld10.objects.none()
        else:
            subledger_obj = T01Sld10.objects.filter(division=t01coa10_obj.division)
            if subledger_type:
                subledger_obj = subledger_obj.filter(subledger_type=subledger_type)
            if subledger_cat:
                subledger_obj = subledger_obj.filter(subledger_cat=subledger_cat)

        if self.q:
            subledger_obj = subledger_obj.filter(subledger_name__icontains=self.q)

        return subledger_obj


class GlWorkOrderAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        from ..models.m10_fin_link import T10Wor10

        filter_kwargs = {}
        search_arg = ["wo_name"]

        super(ParentAutocomplete, self).__init__(
            model=T10Wor10,
            field="division__t01coa10_id",
            forward="vou_coa",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )


class InvTypeAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        division_id = self.forwarded.get("division", None)
        if not division_id:
            return T01Voc11.objects.none()

        # division >> vou_type
        qs = T01Voc11.objects.filter(voucher_name__division_id=division_id)
        if self.forwarded.get("prg_type", None):
            qs = qs.filter(voucher_name__prg_type=self.forwarded["prg_type"])

        if self.q:
            qs = qs.filter(
                Q(voucher_type__icontains=self.q)
                | Q(voucher_name__voucher_name__icontains=self.q)
            )
        return qs


class InvoiceAutocomplete(ParentAutocomplete):
    def __init__(self, **kwargs):
        from ebos2210.models.m10_fin_link import T10Tib10

        filter_kwargs = {
            "recurring_status": True,
            "recurr_id": None,
            "inv_type__voucher_name__prg_type": "TIR",
        }
        search_arg = ["inv_type__voucher_name__voucher_name", "inv_type__voucher_type"]
        super(ParentAutocomplete, self).__init__(
            model=T10Tib10,
            field="division_id",
            forward="division",
            search_arg=search_arg,
            filter_kwargs=filter_kwargs,
        )
