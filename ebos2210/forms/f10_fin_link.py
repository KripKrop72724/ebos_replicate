import re
from datetime import date, datetime
from decimal import Decimal

from dal import autocomplete
from django import forms

from ebos2201.models.m01_core_mas import T01Cur11, T01Voc11, T01Voc12

from ..models.m10_fin_link import T10Gld10, T10Gld11


class T10Gld10Form(forms.ModelForm):
    prg_type = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = T10Gld10
        fields = (
            "prg_type",
            "division",
            "vou_num",
            "vou_type",
            "vou_date",
            "comment1",
            "comment2",
            "vou_curr",
            "vou_hdr_ref",
            "subledger",
            "issued_to",
            "issued_ref",
        )
        widgets = {
            "vou_type": autocomplete.ModelSelect2(
                url="ebos2210:vou_type-autocomplete",
                forward=["division", "prg_type"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a vou type"
                },
            )
        }

    def clean(self):
        super().clean()

        # Check for debit = credit
        total_bcurr_debit, total_bcurr_credit = 0, 0
        total_fcurr_debit, total_fcurr_credit = 0, 0
        if self.cleaned_data.get("division") or self.instance:
            if div_curr := self.instance.division:
                base_curr = div_curr.currency
            elif self.cleaned_data.get("division"):
                base_curr = self.cleaned_data.get("division").currency
            else:
                base_curr = None

            # Validation for base currency
            if self.cleaned_data["vou_curr"] == base_curr:
                bcurr_db_regex = re.compile(r"^gld_header_set-(\d+)-bcurr_debit$")
                bcurr_cr_regex = re.compile(r"^gld_header_set-(\d+)-bcurr_credit$")
                for k, v in self.data.items():
                    bcurr_db_match = re.match(bcurr_db_regex, k)
                    bcurr_cr_match = re.match(bcurr_cr_regex, k)
                    try:
                        if bcurr_db_match:
                            total_bcurr_debit += float(v)
                        if bcurr_cr_match:
                            total_bcurr_credit += float(v)
                    except:
                        pass

                if total_bcurr_debit != total_bcurr_credit:
                    raise forms.ValidationError("Bcurr debit and credit are not equal.")

                if (
                    Decimal(total_bcurr_debit) + Decimal(total_bcurr_credit)
                ) <= Decimal("0.00"):
                    raise forms.ValidationError("Total cannot be 0.")
            else:
                # Validation for foreign currency
                fcurr_db_regex = re.compile(r"^gld_header_set-(\d+)-fcurr_debit$")
                fcurr_cr_regex = re.compile(r"^gld_header_set-(\d+)-fcurr_credit$")

                for k, v in self.data.items():
                    fcurr_db_match = re.match(fcurr_db_regex, k)
                    fcurr_cr_match = re.match(fcurr_cr_regex, k)
                    try:
                        if fcurr_db_match:
                            total_fcurr_debit += float(v)
                        if fcurr_cr_match:
                            total_fcurr_credit += float(v)
                    except:
                        pass

                if total_fcurr_debit != total_fcurr_credit:
                    raise forms.ValidationError("fcurr debit and credit are not equal.")

                if (
                    Decimal(total_fcurr_debit) + Decimal(total_fcurr_credit)
                ) <= Decimal("0.00"):
                    raise forms.ValidationError("Total cannot be 0.")

        if self.instance and self.instance.pk:
            vou_date = self.instance.vou_date
        else:
            vou_date = self.cleaned_data["vou_date"]

        # Validation for get currency rate
        foreign_curr = (
            None
            if self.cleaned_data["vou_curr"] == base_curr
            else self.cleaned_data["vou_curr"]
        )
        try:
            if foreign_curr is None or foreign_curr == base_curr:
                curr_rate = 0
            else:
                if type(vou_date) == "str":
                    vou_date = datetime.strptime(vou_date, "%Y-%m-%d")
                curr_rate = T01Cur11.get_curr_rate(
                    conv_curr_from=foreign_curr,
                    conv_curr_to=base_curr,
                    rate_as_of=vou_date,
                    module="gl",
                )
        except Exception as err:
            raise forms.ValidationError(err)

        # Next number method
        # should run after all field validation
        try:
            if self.instance and self.instance.pk is None:
                self.cleaned_data["vou_num"] = self.check_next_number(
                    self.cleaned_data["vou_type"], vou_date
                )
        except Exception as ex:
            raise forms.ValidationError(ex)

    def check_next_number(self, vou_type, voc_date):
        
        """
        Discussion: 08-March-2023
        Pre audit close    audit close    voucher_cat
            False              False        1, 2  allow
            True               False        3,4  allow
            False              True              Error ("Pre audit skipped, audit closed, no entries allowed.")
            True               True              Error ("Audit closed, no entries allowed.")

        """
        
        # from voucher date find year and period
        year = voc_date.year
        period = voc_date.month

        # filter T01VOC12 matching voc_type, year, period (ie month)
        # if record not found THEN send message 'Period not opened for voucher entry'
        voucher_objs = T01Voc12.objects.filter(
            voucher_type=vou_type, year_num=year, period_num=period
        )

        if voucher_objs.count() > 1:
            raise Exception("Duplicate setup for this voucher type.")
        elif voucher_objs.count() > 0:
            voucher_obj = voucher_objs[0]
            if voucher_obj.lock_flag:
                raise ValueError("Voucher locked.")
            elif (
                not voucher_obj.pre_audit_close
                and not voucher_obj.audit_close
                and voucher_obj.voucher_type.voucher_cat not in ["1", "2"]
            ):
                raise ValueError("No entries allowed.")
            elif (
                voucher_obj.pre_audit_close
                and not voucher_obj.audit_close
                and voucher_obj.voucher_type.voucher_cat not in ["3", "4"]
            ):
                raise ValueError("Year closed, please enter audit adjustment entries.")
            elif (
                not voucher_obj.pre_audit_close
                and voucher_obj.audit_close
            ):
                raise ValueError("Pre audit skipped, audit closed, no entries allowed.")
            elif (
                voucher_obj.pre_audit_close
                and voucher_obj.audit_close
            ):
                raise ValueError("Audit closed, no entries allowed.")
        else:
            raise Exception("Period not opened for voucher entry")


class T10Gld11Form(forms.ModelForm):
    vou_type_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        vou_type_val = None
        instance = kwargs.get("instance", None)

        if instance:
            vou_type_val = instance.vou_id.vou_type
        else:
            data = kwargs.get("data", None)
            if data and data.get("vou_type"):
                vou_type_val = T01Voc11.objects.get(id=data["vou_type"])

        if vou_type_val:
            kwargs["initial"] = {"vou_type_id": vou_type_val.id}

        super(T10Gld11Form, self).__init__(*args, **kwargs)

    class Meta:
        model = T10Gld11
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
        widgets = {
            "vou_coa": autocomplete.ModelSelect2(
                url="ebos2210:vou_coa-autocomplete",
                forward=["vou_type_id"],
                attrs={"data-placeholder": "Please select vou coa"},
            ),
            "vou_subledger": autocomplete.ModelSelect2(
                url="ebos2210:vou_subledger-autocomplete",
                forward=["vou_coa"],
                attrs={"data-placeholder": "Please select vou subledger"},
            ),
            "work_order": autocomplete.ModelSelect2(
                url="ebos2210:work_order-autocomplete",
                forward=["vou_coa"],
                attrs={"data-placeholder": "Please select work order"},
            ),
        }
