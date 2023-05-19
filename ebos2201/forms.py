from dal import autocomplete
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from ebos2201.models.m01_core_mas import T01Voc11, T01VocC10, T01VocC12

from .models.m01_fin_mas import T01Coa10, T01Sld10


class T01VocC10Form(forms.ModelForm):
    PRG_CHOICE = (
        ("", "--------"),
        ("GLA", "GL Allocation"),
        ("RAL", "Receipt Allocation"),
        ("ARV", "Allocate and Receive"),
        ("PAL", "Payment Allocation"),
        ("TIR", "Tax Invoice Receivable"),
        ("TIP", "Tax Invoice Payable"),
        ("API", "Payable Invoice"),
        ("APV", "Allocate and Pay"),
        ("ARI", "Receivable Invoice"),
        ("CRN", "Credit Note"),
        ("DBN", "Debit Note"),
        ("BPV", "Bank Payment Voucher"),
        ("CPV", "Cash Payment Voucher"),
        ("BRV", "Bank Receipt Voucher"),
        ("JVM", "Journal Vocuher"),
        ("CRV", "Cash Receipt Voucher"),
    )
    prg_type = forms.ChoiceField(choices=PRG_CHOICE)

    class Meta:
        model = T01VocC10
        fields = (
            "division",
            "prg_type",
            "system_num",
            "voucher_name",
            "subledger_cat",
            "subledger_type",
            "inv_trn_toacc",
            "match_with_gr",
        )


class T01VocC12Form(forms.ModelForm):
    try:
        voucher_type = forms.ModelChoiceField(
            queryset=T01Voc11.objects.filter(voucher_name__proxy_code="voc")
        )
    except:
        voucher_type = forms.ModelChoiceField(queryset=T01Voc11.objects.none())

    class Meta:
        model = T01VocC12
        fields = (
            "voucher_type",
            "year_num",
            "voucher_prefix",
            "voucher_suffix",
            "starting_num",
            "ending_num",
            "next_num",
            "period_num",
            "lock_flag",
            "pre_audit_close",
            "audit_close",
        )


class T01Coa10Form(forms.ModelForm):
    class Meta:
        model = T01Coa10
        fields = (
            "division",
            "parent",
            "account_name",
            "account_type",
            "account_group",
            "coa_control",
            "account_num",
            "coa_sl_cat",
            "coa_sl_type",
            "activity_group",
            "cashflow_group",
        )
        widgets = {
            "parent": autocomplete.ModelSelect2(
                url="ebos2201:parent_coa-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select coa"},
            ),
            "coa_sl_type": autocomplete.ModelSelect2(
                url="ebos2201:subledger_type-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select subledger type"},
            ),
            "activity_group": autocomplete.ModelSelect2(
                url="ebos2201:activity_group-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select an activity group"},
            ),
            "cashflow_group": autocomplete.ModelSelect2(
                url="ebos2201:cashflow_group-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select an cashflow group"},
            ),
        }

    def clean(self):
        data = self.cleaned_data
        if data.get("parent"):
            data["account_group"] = data["parent"].account_group
        if data.get("coa_control") == "1":
            data["coa_sl_cat"] = None
            data["coa_sl_type"] = None

        return super().clean()


class T01Sld10Form(forms.ModelForm):
    class Meta:
        model = T01Sld10
        fields = (
            "division",
            "subledger_name",
            "subledger_code",
            "subledger_type",
            "subledger_cat",
            "invoice_address1",
            "invoice_address2",
            "invoice_address3",
            "ship_to_address1",
            "ship_to_address2",
            "ship_to_address3",
            "telephone1",
            "telephone2",
            "fax",
            "primary_contact_name",
            "primary_email",
            "primary_mobile",
            "commission_percent",
            "credit_days",
            "credit_days_from",
            "mode_of_payment",
            "credit_limit",
            "credit_open",
            "due_amount",
            "as_of_date",
            "key_account_flag",
        )
        widgets = {
            "subledger_type": autocomplete.ModelSelect2(
                url="ebos2201:subledger_type-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select subledger type"},
            ),
        }
