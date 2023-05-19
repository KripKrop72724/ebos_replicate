import re

from dal import autocomplete
from django import forms

from ebos2201.models.m01_core_mas import T01Div10, T01Voc11
from ebos2201.models.m01_fin_mas import T01Coa10, T01Glc10, T01Sld10
from ebos2210.models.m10_fin_ap import T10Pps10, T10Tip10
from ebos2210.models.m10_fin_ar import T10Rin10, T10Tir10
from ebos2210.models.m10_fin_fa import T10Fat10
from ebos2210.models.m10_fin_gl import T10Abr10, T10Alc10, T10Gla10, T10Tic10, T10Tic11

from ..models.m10_fin_link import T10Gld10, T10Gld11, T10Tib10
from .f10_fin_link import T10Gld10Form, T10Gld11Form


class T10Jvm10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "JVM"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)

    class Meta(T10Gld10Form.Meta):
        exclude = (
            "subledger",
            "issued_to",
            "issued_ref",
        )


class T10Bpv10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "BPV"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class T10Cpv10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "CPV"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class BpvInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "cc_number",
            "cc_expiry_date",
            "cc_auth_code",
            "chq_num",
            "chq_date",
            "chq_status",
            "alloc_amt_tot",
            "alloc_date",
        )

    def clean(self):
        """
        if base currency credit amount > 0 and base currency debit=0, coa account_type == bank, cash, card
        """
        cleaned_data = super().clean()
        vou_coa = self.cleaned_data.get("vou_coa")
        bcurr_debit = self.cleaned_data.get("bcurr_debit")
        bcurr_credit = self.cleaned_data.get("bcurr_credit")
        if (bcurr_debit and bcurr_debit > 0 and vou_coa == None) or (
            bcurr_credit and bcurr_credit > 0 and vou_coa == None
        ):
            self.add_error("vou_coa", "Please enter a valid chart of account.")

        if vou_coa:
            account_type = vou_coa.account_type
            if bcurr_credit > 0 and bcurr_debit in [0, 0.00, 0.0]:
                if account_type not in ["2", "3", "4"]:
                    self.add_error(
                        "vou_coa", "Coa account type should be bank, cash or card."
                    )

        return cleaned_data


class CpvInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )

    def clean(self):
        """
        if base currency credit amount > 0 and base currency debit=0, coa account_type == cash
        """
        cleaned_data = super().clean()
        vou_coa = self.cleaned_data.get("vou_coa")
        bcurr_debit = self.cleaned_data.get("bcurr_debit")
        bcurr_credit = self.cleaned_data.get("bcurr_credit")
        if (bcurr_debit and bcurr_debit > 0 and vou_coa == None) or (
            bcurr_credit and bcurr_credit > 0 and vou_coa == None
        ):
            self.add_error("vou_coa", "Please enter a valid chart of account.")

        if vou_coa:
            account_type = vou_coa.account_type
            if bcurr_credit > 0 and bcurr_debit in [0, 0.00, 0.0]:
                if account_type not in ["3", "4"]:
                    self.add_error(
                        "vou_coa", "Coa account type should be cash or card."
                    )

        return cleaned_data


class T10Brv10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "BRV"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class T10Crv10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "CRV"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class BrvInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "chq_num",
            "chq_date",
            "chq_status",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )

    def clean(self):
        """
        if baseCurr debit amount > 0 and basecurr credit amount=0 coa account_type == bank, cash, card
        """
        cleaned_data = super().clean()
        vou_coa = self.cleaned_data.get("vou_coa")
        bcurr_debit = self.cleaned_data.get("bcurr_debit")
        bcurr_credit = self.cleaned_data.get("bcurr_credit")
        if (bcurr_debit and bcurr_debit > 0 and vou_coa == None) or (
            bcurr_credit and bcurr_credit > 0 and vou_coa == None
        ):
            self.add_error("vou_coa", "Please enter a valid chart of account.")

        if vou_coa:
            account_type = vou_coa.account_type
            if bcurr_debit > 0 and bcurr_credit in [0, 0.00, 0.0]:
                if account_type not in ["2", "3", "4"]:
                    self.add_error(
                        "vou_coa", "Coa account type should be bank, cash or card."
                    )

        return cleaned_data


class CrvInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )

    def clean(self):
        """
        if basecurr debit amount > 0 and basecurr credit =0 , coa account_type == cash
        """
        cleaned_data = super().clean()
        vou_coa = self.cleaned_data.get("vou_coa")
        bcurr_debit = self.cleaned_data.get("bcurr_debit")
        bcurr_credit = self.cleaned_data.get("bcurr_credit")
        if (bcurr_debit and bcurr_debit > 0 and vou_coa == None) or (
            bcurr_credit and bcurr_credit > 0 and vou_coa == None
        ):
            self.add_error("vou_coa", "Please enter a valid chart of account.")

        if vou_coa:
            account_type = vou_coa.account_type
            if bcurr_debit > 0 and bcurr_credit in [0, 0.00, 0.0]:
                if account_type not in ["3", "4"]:
                    self.add_error(
                        "vou_coa", "Coa account type should be cash or card."
                    )

        return cleaned_data


# Debit note
class T10Dbn10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "DBN"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class DbnInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )


# Credit note
class T10Crn10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "CRN"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class CrnInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )


# Account Receivable Invoice
class T10Ari10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "ARI"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class AriInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )


# Account Payable Invoice
class T10Api10Form(T10Gld10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "API"}
        super(T10Gld10Form, self).__init__(*args, **kwargs)


class ApiInlineForm(T10Gld11Form):
    class Meta(T10Gld11Form.Meta):
        fields = (
            "vou_type_id",
            "vou_coa",
            "vou_subledger",
            "bcurr_debit",
            "bcurr_credit",
            "narration",
            "vou_line_ref",
            "work_order",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "alloc_amt_tot",
            "alloc_date",
        )


""" Fixed asset forms """


class T10Fat10Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(T10Fat10Form, self).__init__(*args, **kwargs)
        try:
            self.fields["doc_type"] = forms.ModelChoiceField(
                queryset=T01Voc11.objects.filter(voucher_name__prg_type="FAT")
            )
            gl_c = T01Glc10.objects.get(id=int(self.data["gl_code"])).description
            if gl_c == "Disposed":
                self.fields["salvage_amt"].widget.attrs["disabled"] = True
            elif gl_c == "Scrap":
                self.fields["disposal_amt"].widget.attrs["disabled"] = True
            else:
                self.fields["salvage_amt"].widget.attrs["disabled"] = True
                self.fields["disposal_amt"].widget.attrs["disabled"] = True
        except Exception as ex:
            pass

    class Meta:
        model = T10Fat10
        fields = (
            "asset_id",
            "doc_type",
            "doc_num",
            "doc_date",
            "narration",
            "gl_code",
            "disposal_amt",
            "salvage_amt",
            "issued_division",
            "issued_department",
            "issued_warehouse",
            "issue_qty",
            "expected_return_dt",
            "recv_division",
            "recv_department",
            "recv_warehouse",
            "recv_qty",
            "actual_return_dt",
            "project_id",
            "post_flag",
            "gl_ref",
        )

    def clean(self):
        cleaned_data = super().clean()
        gl_code = self.cleaned_data.get("gl_code")

        if gl_code:
            if (
                gl_code.description == "Disposed"
                and self.cleaned_data.get("disposal_amt") is None
            ):
                self.add_error("disposal_amt", "Please enter the disposal amount.")
            elif (
                gl_code.description == "Scrap"
                and self.cleaned_data.get("salvage_amt") is None
            ):
                self.add_error("salvage_amt", "Please enter the salvage amount.")
        return cleaned_data


""" Recurring sales invoice form """


class T10Rin10Form(forms.ModelForm):
    class Meta:
        model = T10Rin10
        fields = (
            "division",
            "invoice",
            "contract_months",
            "frequency",
            "recurring_from",
            "status",
            "allocated_dt",
        )
        widgets = {
            "invoice": autocomplete.ModelSelect2(
                url="ebos2210:invoice-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select subledger"},
            )
        }


""" Prepayment Amortization (schedule) form """


class T10Pps10Form(forms.ModelForm):
    class Meta:
        model = T10Pps10
        fields = (
            "division",
            "voucher_id",
            "prepay_coa",
            "prepay_amt",
            "allocated_coa",
            "frequency",
            "prepay_schedule_from",
            "prepay_months",
            "allocated_dt",
            "allocated_amt",
            "status",
            "gl_code",
        )
        widgets = {
            "voucher_id": autocomplete.ModelSelect2(
                url="ebos2210:vou_id-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select vou id"},
            ),
            "prepay_coa": autocomplete.ModelSelect2(
                url="ebos2210:prepay_coa-autocomplete",
                forward=["voucher_id"],
                attrs={"data-placeholder": "Please select coa"},
            ),
            "allocated_coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select coa"},
            ),
        }


class T10Tic10Form(forms.ModelForm):
    division = forms.ModelChoiceField(queryset=T01Div10.objects.none())
    from_coa = forms.ModelChoiceField(queryset=T01Coa10.objects.none())
    ic_coa = forms.ModelChoiceField(queryset=T01Coa10.objects.none())
    from_sl = forms.ModelChoiceField(queryset=T01Sld10.objects.none())

    def __init__(self, *args, **kwargs):
        super(T10Tic10Form, self).__init__(*args, **kwargs)
        try:
            if self.data["company"]:
                division = forms.ModelChoiceField(
                    queryset=T01Div10.objects.filter(company=self.data["company"])
                )

            if self.data["division"]:
                coa_qs = T01Coa10.objects.filter(
                    division=self.data["division"], coa_control="2"
                )
                from_coa = forms.ModelChoiceField(queryset=coa_qs)
                ic_coa = forms.ModelChoiceField(queryset=coa_qs)
                from_sl = forms.ModelChoiceField(
                    queryset=T01Sld10.objects.filter(division=self.data["division"])
                )

            self.fields["division"] = division
            self.fields["from_coa"] = from_coa
            self.fields["ic_coa"] = ic_coa
            self.fields["from_sl"] = from_sl
        except:
            pass

    class Meta:
        model = T10Tic10
        fields = (
            "company",
            "division",
            "vou_type",
            "from_coa",
            "from_sl",
            "ic_coa",
            "vou_dtfrom",
            "vou_dtto",
            "from_amt",
            "flag_db_cr",
            "gl_code",
            "aa_code",
        )


class T10Tic11Form(forms.ModelForm):
    class Meta:
        model = T10Tic11
        fields = (
            "company",
            "division",
            "vou_type",
            "to_coa",
            "to_subledger",
            "ic_coa",
            "percent_alloc",
            "to_amt",
            "alloc_date",
            "narration",
            "gl_code",
            "aa_code",
        )

    def clean(self):
        super().clean()

        # Check for percent allocation total <= 100 %
        total_perc_alloc = 0
        perc_alloc_regex = re.compile(r"^inter_com_set-(\d+)-percent_alloc$")

        for k, v in self.data.items():
            perc_alloc_match = re.match(perc_alloc_regex, k)
            try:
                if perc_alloc_match:
                    total_perc_alloc += float(v)
            except:
                pass

        if total_perc_alloc > 100:
            raise forms.ValidationError(
                "The percent allocation total must be less than or equal 100."
            )


""" Tax invoice header form """


class T10Tib10Form(forms.ModelForm):
    prg_type = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = T10Tib10
        fields = (
            "prg_type",
            "division",
            "inv_curr",
            "inv_type",
            "inv_date",
            "due_date",
            "inv_num",
            "hdr_ref",
            "hdr_comment",
            "subledger",
            "pmt_term",
            "gl_code",
            "recurring_status",
        )
        widgets = {
            "inv_type": autocomplete.ModelSelect2(
                url="ebos2210:inv_type-autocomplete",
                forward=["division", "prg_type"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a inv type"
                },
            )
        }


""" Tax invoice AP header form """


class T10Tip10Form(T10Tib10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "TIP"}
        super(T10Tib10Form, self).__init__(*args, **kwargs)

    class Meta(T10Tib10Form.Meta):
        exclude = ("recurring_status",)


""" Tax invoice AR header form """


class T10Tir10Form(T10Tib10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "TIR"}
        super(T10Tib10Form, self).__init__(*args, **kwargs)


"""Allocation forms"""


class T10Alc10Form(forms.ModelForm):
    prg_type = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(T10Alc10Form, self).__init__(*args, **kwargs)
        if self.fields.get("subledger"):
            subledger_field = self.fields["subledger"]
            subledger_field.widget.can_add_related = False
            subledger_field.widget.can_change_related = False
            subledger_field.widget.can_delete_related = False

        if self.fields.get("coa"):
            coa_field = self.fields["coa"]
            coa_field.widget.can_add_related = False
            coa_field.widget.can_change_related = False
            coa_field.widget.can_delete_related = False

    class Meta:
        model = T10Alc10
        fields = (
            "prg_type",
            "division",
            "vou_type",
            "vou_num",
            "vou_date",
            "coa",
            "subledger",
            "date_choice",
            "date_from",
            "date_to",
            "alloc_lock_flag",
            "currency",
            "hdr_comment",
            "issued_to",
            "tot_amount",
            "line_narration",
            "chq_num",
            "chq_date",
        )
        widgets = {
            "vou_type": autocomplete.ModelSelect2(
                url="ebos2210:vou_type-autocomplete",
                forward=["division", "prg_type"],
                attrs={
                    "data-placeholder": "Please select a vou type",
                },
            ),
            "coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={"data-placeholder": "Please select a COA"},
            ),
        }

    def clean(self):
        super().clean()
        try:
            # Check for debit = credit
            total_debit_alloc, total_credit_alloc = 0, 0

            debit_alloc_regex = re.compile(r"^allocation_db-(\d+)-debit_alloc$")
            credit_alloc_regex = re.compile(r"^allocation_cr-(\d+)-credit_alloc$")
            for k, v in self.data.items():
                debit_alloc_match = re.match(debit_alloc_regex, k)
                credit_alloc_match = re.match(credit_alloc_regex, k)
                try:
                    if debit_alloc_match:
                        total_debit_alloc += float(v)
                    if credit_alloc_match:
                        total_credit_alloc += float(v)
                except:
                    pass

            if total_debit_alloc != total_credit_alloc:
                raise forms.ValidationError("Allocated debit and credit not matching.")
        except Exception as e:
            raise forms.ValidationError(e)


class T10Gla10Form(T10Alc10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "GLA"}
        super().__init__(*args, **kwargs)

    class Meta(T10Alc10Form.Meta):
        fields = T10Alc10Form.Meta.fields


class T10Pal10Form(T10Alc10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "PAL"}
        super().__init__(*args, **kwargs)

    class Meta(T10Alc10Form.Meta):
        fields = T10Alc10Form.Meta.fields


class T10Ral10Form(T10Alc10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "RAL"}
        super().__init__(*args, **kwargs)

    class Meta(T10Alc10Form.Meta):
        fields = T10Alc10Form.Meta.fields


class T10Apv10Form(T10Alc10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "APV"}
        super().__init__(*args, **kwargs)

    class Meta(T10Alc10Form.Meta):
        fields = T10Alc10Form.Meta.fields


class T10Arv10Form(T10Alc10Form):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = {"prg_type": "ARV"}
        super().__init__(*args, **kwargs)

    class Meta(T10Alc10Form.Meta):
        fields = T10Alc10Form.Meta.fields


class T10Abr10Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id is None:
            self.fields["import_bank_stmt"].required = True

    class Meta:
        model = T10Abr10
        exclude = ("proxy_code",)
