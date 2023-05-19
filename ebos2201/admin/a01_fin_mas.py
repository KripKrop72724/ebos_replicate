from datetime import datetime

from dal import autocomplete
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from ebos2201.views.v01_coa_master_print import COAMaster

from ..forms import T01Coa10Form, T01Sld10Form
from ..models.m01_fin_mas import (
    T01Act10,
    T01Bnk10,
    T01Cdf10,
    T01Cfl10,
    T01Coa10,
    T01Div10,
    T01Glc10,
    T01Lan10,
    T01Mop10,
    T01Sld10,
    T01SldM10,
    T01Slm10,
    T01Slm11,
    T01Slt10,
    T01Stp10,
)


# Division filter: Showing division only for requested user
class DivisionListFilter(admin.SimpleListFilter):
    title = _("Division")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "division"
    dependent_key = None

    def lookups(self, request, model_admin):
        try:
            self.dependent_key = model_admin.dependent_key
        except:
            pass
        return (
            (obj.division_name, obj)
            for obj in T01Div10.objects.filter(user=request.user)
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            if self.dependent_key:
                kwargs = {
                    f"{self.dependent_key}__division__division_name": self.value()
                }
                return queryset.filter(**kwargs)
            return queryset.filter(division__division_name=self.value())


# Base Model for all
class T01BaseAdmin(admin.ModelAdmin):
    list_filter = [DivisionListFilter]
    change_form_template = "ebos2201/admin/t01_base_change_form.html"

    class Media:
        css = {
            "all": ("css/admin.css",),
        }
        js = ("admin/js/common.js",)

    def get_queryset(self, request):
        user = request.user
        try:
            if self.dependent_key:
                kwargs = {f"{self.dependent_key}__division__user": user}
                return super().get_queryset(request).filter(**kwargs)
        except:
            return super().get_queryset(request).filter(division__user=user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if form.base_fields.get("division", None):
            qs = T01Div10.objects.filter(user=request.user)
            form.base_fields["division"].widget = autocomplete.ModelSelect2(
                url="ebos2201:division-autocomplete",
                attrs={"data-placeholder": "Please select a division"},
            )
            if subledger := form.base_fields.get("subledger"):
                subledger.widget = autocomplete.ModelSelect2(
                    url="ebos2201:subledger-autocomplete",
                    forward=["division"],
                    attrs={"data-placeholder": "Please select a subledger"},
                )
            if qs.count() == 1:
                form.base_fields["division"].initial = qs[0]
                if vou_curr := form.base_fields.get("vou_curr"):
                    vou_curr.initial = qs[0].currency
                if inv_curr := form.base_fields.get("inv_curr"):
                    inv_curr.initial = qs[0].currency

            if vou_date := form.base_fields.get("vou_date"):
                vou_date.initial = datetime.today()
            if inv_date := form.base_fields.get("inv_date"):
                inv_date.initial = datetime.today()
        return form

    def csv_button(self, obj):
        return format_html(
            "<a href='{}' class='button print-btn'>Download</a>",
            settings.SITE_DOMAIN + settings.MEDIA_URL + str(obj.file_csv),
        )

    csv_button.short_description = "CSV file"

    def pdf_button(self, obj):
        return format_html(
            "<a href='{}' class='button print-btn' target='_blank'>Print</a>",
            settings.SITE_DOMAIN + settings.MEDIA_URL + str(obj.file_pdf),
        )

    pdf_button.short_description = "PDF file"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add/get_division_currency/<int:division>/", self.get_division_currency
            ),
        ]
        return custom_urls + urls

    def get_division_currency(self, request, division):
        div_curr = T01Div10.objects.get(id=division).currency
        result = {"division_curr": div_curr.id}
        return JsonResponse(result)


admin.site.register(T01Stp10)


class T01Bnk10Admin(T01BaseAdmin):
    list_display = ("division", "bank_name", "bank_branch")


# Chart of Accounts
class T01Coa10Admin(MPTTModelAdmin, T01BaseAdmin):
    form = T01Coa10Form
    fields = (
        "division",
        "parent",
        ("account_name", "account_num"),
        ("account_group", "account_type", "coa_control"),
        ("coa_sl_cat", "coa_sl_type"),
        ("activity_group", "cashflow_group"),
    )
    list_display = (
        "parent",
        "account_num",
        "account_name",
        "level",
        "account_type",
        "account_group",
        "coa_control",
        "coa_sl_cat",
        "coa_sl_type",
        "activity_group",
        "cashflow_group",
        "division",
    )
    list_display_links = (
        "parent",
        "account_num",
        "account_name",
        "level",
        "account_type",
        "account_group",
        "coa_control",
        "coa_sl_cat",
        "coa_sl_type",
        "activity_group",
        "cashflow_group",
        "division",
    )
    search_fields = [
        "account_name",
        "level",
        "account_num",
        "coa_sl_cat",
        "coa_sl_type__sl_type_desc",
        "activity_group__activity_name",
        "cashflow_group__cashflow_desc",
        "division__division_name",
    ]
    actions = ["print_coa_master"]
    change_form_template = "ebos2201/admin/t01_coa_change_form.html"

    def get_list_filter(self, request):
        list_filter_fields = super(T01BaseAdmin, self).get_list_filter(request)
        return list_filter_fields + ['coa_control',]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("add/get_parent_account_grp/<int:parentId>/", self.get_account_group),
            path(
                "<int:id>/change/get_parent_account_grp/<int:parentId>/",
                self.get_account_group,
            ),
        ]
        return custom_urls + urls

    def get_account_group(self, request, id=None, parentId=None):
        result = {"parent_account_grp": T01Coa10.objects.get(id=parentId).account_group}
        return JsonResponse(result)

    """ Print Voucher custom action functionality """

    def print_coa_master(self, request, queryset):
        for query in queryset:
            COAMaster.get_all_accounts(query.division)
            pdf_obj = COAMaster.init_pdf(query.division)
            return pdf_obj

    print_coa_master.short_description = "Print COA Master"


# SubLedger Master
class T01Sld10Admin(T01BaseAdmin):
    form = T01Sld10Form
    list_display = (
        "subledger_name",
        "subledger_no",
        "subledger_code",
        "subledger_type",
        "subledger_cat",
        "primary_email",
        "primary_mobile",
        "division",
    )
    list_display_links = (
        "subledger_name",
        "subledger_no",
        "subledger_code",
        "subledger_type",
        "subledger_cat",
        "division",
        "primary_email",
        "primary_mobile",
    )
    readonly_fields = ["credit_open", "due_amount", "as_of_date"]
    search_fields = [
        "subledger_name",
        "subledger_no",
        "subledger_code",
        "subledger_type__sl_type_desc",
        "division__division_name",
        "primary_email",
        "primary_mobile",
    ]
    exclude = ("proxy_code",)


# Subledger Master proxy
class T01SldM10Admin(T01Sld10Admin):
    model = T01Sld10


# SubLedger Type
class T01Slt10Admin(T01BaseAdmin):
    list_display = ("sl_type_desc", "sl_type_code", "division")


# GL Code
class T01Glc10Admin(admin.ModelAdmin):
    list_display = (
        "gl_code",
        "description",
        "gl_category",
    )


# Credit Days From
class T01Cdf10Admin(admin.ModelAdmin):
    list_display = ("credit_days_from", "document_type")


# Mode of Pay
class T01Mop10Admin(admin.ModelAdmin):
    list_display = ("mode_of_pay", "mop_code")


# Cashflow Setup
class T01Cfl10Admin(MPTTModelAdmin):
    list_display = ("cashflow_desc", "level", "cashflow_cat")


#
class T01Act10Admin(MPTTModelAdmin, T01BaseAdmin):
    list_display = ("activity_name", "level", "division")


# Sales Person Skill
class T01Slm11Inline(admin.TabularInline):
    model = T01Slm11
    fields = ("language", "read", "write", "speak")


# Languages
class T01Lan10Admin(admin.ModelAdmin):
    list_display = ("language_name",)


# Sales Person
class T01Slm10Admin(admin.ModelAdmin):
    inlines = [T01Slm11Inline]
    list_display = (
        "first_name",
        "last_name",
        "mobile",
        "telephone",
        "email",
        "commission_percent",
        "gender",
        "nationality",
        "subledger",
    )


admin.site.register(T01Bnk10, T01Bnk10Admin)
admin.site.register(T01Coa10, T01Coa10Admin)
admin.site.register(T01Sld10, T01Sld10Admin)
admin.site.register(T01SldM10, T01SldM10Admin)
admin.site.register(T01Slt10, T01Slt10Admin)
admin.site.register(T01Glc10, T01Glc10Admin)
admin.site.register(T01Mop10, T01Mop10Admin)
admin.site.register(T01Cfl10, T01Cfl10Admin)
admin.site.register(T01Act10, T01Act10Admin)
admin.site.register(T01Cdf10, T01Cdf10Admin)
admin.site.register(T01Slm10, T01Slm10Admin)
admin.site.register(T01Lan10, T01Lan10Admin)
