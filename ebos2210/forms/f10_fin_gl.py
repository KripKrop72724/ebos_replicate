from dal import autocomplete
from django import forms

from ..models.m10_fin_gl import *


class T10GlrB01Form(forms.ModelForm):
    class Meta:
        model = T10GlrB01
        exclude = ("rpt_code", "vou_curr", "aging1", "aging2", "aging3")
        widgets = {
            "coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a COA",
                },
            )
        }


class T10Glc01Form(forms.ModelForm):
    class Meta:
        model = T10Glc01
        exclude = ("rpt_code", "vou_curr", "aging1", "aging2", "aging3", "file_csv")
        widgets = {
            "coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a COA"
                },
            )
        }


class T10Stm01Form(forms.ModelForm):
    class Meta:
        model = T10Stm01
        exclude = ("rpt_code", "coa", "aging1", "aging2", "aging3", "file_csv")


class T10Stm02Form(forms.ModelForm):
    class Meta:
        model = T10Stm02
        exclude = ("rpt_code", "coa", "aging1", "aging2", "aging3", "file_csv")


class T10SlCoa01Form(forms.ModelForm):
    class Meta:
        model = T10SlCoa01
        exclude = (
            "rpt_code",
            "dt_from",
            "subledger",
            "vou_curr",
            "aging1",
            "aging2",
            "aging3",
            "file_csv",
        )
        widgets = {
            "coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a COA"
                },
            ),
        }


class T10SlCoa02Form(forms.ModelForm):
    class Meta:
        model = T10SlCoa02
        exclude = (
            "rpt_code",
            "subledger",
            "vou_curr",
            "aging1",
            "aging2",
            "aging3",
            "file_csv",
        )
        widgets = {
            "coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a COA"
                },
            ),
        }


class T10AgRpt01Form(forms.ModelForm):
    class Meta:
        model = T10AgRpt01
        exclude = ("rpt_code", "coa", "dt_from", "vou_curr")


class T10LdgAcc01Form(forms.ModelForm):
    class Meta:
        model = T10LdgAcc01
        exclude = (
            "rpt_code",
            "coa",
            "dt_from",
            "vou_curr",
            "aging1",
            "aging2",
            "aging3",
            "file_csv",
        )


class T10ChrAcc01Form(forms.ModelForm):
    class Meta:
        model = T10ChrAcc01
        exclude = (
            "rpt_code",
            "subledger",
            "dt_from",
            "vou_curr",
            "aging1",
            "aging2",
            "aging3",
            "file_csv",
        )
        widgets = {
            "coa": autocomplete.ModelSelect2(
                url="ebos2210:postable_coa-autocomplete",
                forward=["division"],
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Please select a COA"
                },
            ),
        }
