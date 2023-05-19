from django.contrib import admin, messages
from django.http import JsonResponse
from django.urls import path
from django.utils.translation import ngettext

from ebos2201.admin.a01_fin_mas import T01BaseAdmin
from ebos2210.forms import T10Fat10Form
from ebos2210.models.m10_fin_fa import *


class T10Fam10Admin(admin.ModelAdmin):
    list_display = [
        "department",
        "warehouse_id",
        "asset_desc",
        "asset_qty",
        "dep_type",
        "current_value",
        "asset_cat",
        "asset_status",
    ]
    fields = (
        "division",
        "department",
        "warehouse_id",
        "asset_desc",
        "asset_pur_doc",
        "asset_pur_date",
        "asset_qty",
        "serial_no",
        "part_no",
        "asset_tag_ref",
        "dep_type",
        "life_months",
        "dep_start_dt",
        "dep_end_dt",
        "dep_months",
        "dep_frequency",
        "dep_percent",
        "asset_value",
        "salvage_amt",
        "last_dep_dt",
        "accum_dep",
        "current_value",
        "disposal_amt",
        "disposal_dt",
        "final_dep",
        "amc_cost",
        "remarks",
        "last_maint_dt",
        "next_maint_dt",
        "amc_renew_dt",
        "warranty_exp_dt",
        "asset_status",
        "subledger",
        "asset_cat",
        "gl_code",
    )
    readonly_fields = [
        "last_dep_dt",
        "accum_dep",
        "current_value",
        "disposal_amt",
        "disposal_dt",
        "final_dep",
        "last_maint_dt",
        "next_maint_dt",
        "asset_status",
        "gl_code",
    ]
    list_filter = ["asset_status", "asset_cat__category_code"]


admin.site.register(T10Fam10, T10Fam10Admin)


class T10Fam11Inline(admin.TabularInline):
    model = T10Fam11


class T10Fam12Inline(admin.TabularInline):
    model = T10Fam12


class T10Srv10Admin(admin.ModelAdmin):
    list_display = [
        "department",
        "warehouse_id",
        "asset_desc",
        "asset_qty",
        "dep_type",
        "current_value",
        "asset_cat",
        "asset_status",
    ]
    readonly_fields = (
        "division",
        "department",
        "warehouse_id",
        "asset_desc",
        "asset_pur_doc",
        "asset_pur_date",
        "asset_qty",
        "serial_no",
        "part_no",
        "asset_tag_ref",
        "dep_type",
        "life_months",
        "dep_start_dt",
        "dep_end_dt",
        "dep_months",
        "dep_frequency",
        "dep_percent",
        "asset_value",
        "salvage_amt",
        "last_dep_dt",
        "accum_dep",
        "current_value",
        "disposal_amt",
        "disposal_dt",
        "final_dep",
        "amc_cost",
        "remarks",
        "last_maint_dt",
        "next_maint_dt",
        "amc_renew_dt",
        "warranty_exp_dt",
        "asset_status",
        "subledger",
        "asset_cat",
        "gl_code",
    )
    list_filter = ["asset_status", "asset_cat__category_code"]
    search_fields = (
        "division__division_name",
        "department__department_name",
        "warehouse_id__warehouse_name",
    )

    inlines = [T10Fam12Inline]

    def has_add_permission(self, request) -> bool:
        return False


admin.site.register(T10Srv10, T10Srv10Admin)


class T10Fat10Admin(admin.ModelAdmin):
    form = T10Fat10Form
    readonly_fields = ["doc_num", "post_flag", "gl_ref"]
    change_form_template = "ebos2210/admin/t10_asset_transaction_change_form.html"

    def get_gl_data(self, request, gl_code):
        return JsonResponse({"gl_data": T01Glc10.objects.get(id=gl_code).description})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("add/get_gl_data/<int:gl_code>/", self.get_gl_data),
        ]
        return custom_urls + urls


admin.site.register(T10Fat10, T10Fat10Admin)


class T10Fap10Admin(admin.ModelAdmin):
    list_display = ["division", "year", "month", "status"]
    list_filter = ["status"]
    actions = ["post_fixed_asset", "unpost_fixed_asset"]

    """Post Fixed Asset custom action functionality"""

    @admin.action(description="Post Fixed Asset")
    def post_fixed_asset(self, request, queryset):
        posted = 0
        for q in queryset:
            if q.status == "unposted":
                depreciation = q.post_depreciation()
                if depreciation:
                    posted += 1

                    # update the status of T10Fap10
                    q.status = "posted"
                    q.save()

        if posted > 0:
            self.message_user(
                request,
                ngettext(
                    "%d successfully posted.",
                    "%d successfully posted.",
                    posted,
                )
                % posted,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "Something wrong", messages.ERROR)

    """UnPost Fixed Asset custom action functionality"""

    @admin.action(description="Unpost Fixed Asset")
    def unpost_fixed_asset(self, request, queryset):
        unposted = 0
        for q in queryset:
            if q.status == "posted":
                depreciation = q.unpost_depreciation()
                if depreciation:
                    unposted += 1

                    # update the status of T10Fap10
                    q.status = "unposted"
                    q.save()

        if unposted > 0:
            self.message_user(
                request,
                ngettext(
                    "%d successfully unposted.",
                    "%d successfully unposted.",
                    unposted,
                )
                % unposted,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "Something wrong", messages.ERROR)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


admin.site.register(T10Fap10, T10Fap10Admin)


class T10Dpn10Admin(admin.ModelAdmin):
    list_display = ["division", "year", "month", "status"]
    list_filter = ["status"]

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


admin.site.register(T10Dpn10, T10Dpn10Admin)


class T10Vah10Admin(admin.ModelAdmin):
    list_display = [
        "department",
        "warehouse_id",
        "asset_desc",
        "asset_qty",
        "dep_type",
        "current_value",
        "asset_cat",
        "asset_status",
    ]
    fields = (
        "division",
        "department",
        "warehouse_id",
        "asset_desc",
        "asset_pur_doc",
        "asset_pur_date",
        "asset_qty",
        "serial_no",
        "part_no",
        "asset_tag_ref",
        "dep_type",
        "life_months",
        "dep_start_dt",
        "dep_end_dt",
        "dep_months",
        "dep_frequency",
        "dep_percent",
        "asset_value",
        "salvage_amt",
        "last_dep_dt",
        "accum_dep",
        "current_value",
        "disposal_amt",
        "disposal_dt",
        "final_dep",
        "amc_cost",
        "remarks",
        "last_maint_dt",
        "next_maint_dt",
        "amc_renew_dt",
        "warranty_exp_dt",
        "asset_status",
        "subledger",
        "asset_cat",
        "gl_code",
    )
    readonly_fields = [
        "last_dep_dt",
        "accum_dep",
        "current_value",
        "disposal_amt",
        "disposal_dt",
        "final_dep",
        "last_maint_dt",
        "next_maint_dt",
        "asset_status",
        "gl_code",
    ]
    list_filter = ["asset_status", "asset_cat__category_code"]

    inlines = [T10Fam11Inline, T10Fam12Inline]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


admin.site.register(T10Vah10, T10Vah10Admin)

# Asset Reports
class T10Avr01Admin(T01BaseAdmin):
    list_display = ("division", "pdf_button")
    exclude = ("rpt_code", "file_csv")
    readonly_fields = ["file_pdf"]


class T10Dar01Admin(T01BaseAdmin):
    list_display = ("division", "pdf_button")
    exclude = ("rpt_code", "file_csv")
    readonly_fields = ["file_pdf"]


admin.site.register(T10Avr01, T10Avr01Admin)
admin.site.register(T10Dar01, T10Dar01Admin)
