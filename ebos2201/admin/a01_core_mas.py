from datetime import date
from gettext import ngettext

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from ebos2201.admin.a01_fin_mas import T01BaseAdmin
from ebos2201.forms import T01VocC10Form, T01VocC12Form
from ebos2201.views.v01_comp_master_print import COMPMaster
from ebos2201.views.v01_month_close_checklist import MonthCloseCheckList

from django.contrib.auth.models import Permission


from ..models.m01_core_mas import (
    T01Atm10,
    T01Cat10,
    T01Cfg10,
    T01Com10,
    T01Cur10,
    T01Cur11,
    T01Dep10,
    T01Div10,
    T01Dsg10,
    T01Nat10,
    T01Slu10,
    T01Uom10,
    T01Uom11,
    T01Voc10,
    T01Voc11,
    T01Voc12,
    T01VocC10,
    T01VocC12,
    T01Whm10,
    User,
)
from ..models.m01_fin_mas import T01Prj10


class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )

    fieldsets = (
        (None, {"fields": ("username", "password", "otp")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "phone_number")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined", "otp_expire_at")}),
    )

    add_fieldsets = ((None, {"fields": ("username", "password1", "password2")}),)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only include permissions from the CustomPermissionModel
        form.base_fields['user_permissions'].queryset = Permission.objects.filter(
            content_type__app_label='ebos2201',  # replace with your app name
            content_type__model='custompermissionmodel',
        )
        return form


admin.site.register(User, UserAdmin)

# Category model
class T01Cat10Admin(admin.ModelAdmin):
    list_display = ("category_code", "category_name", "system_code", "program_code")


# Currency model
class T01Cur10Admin(admin.ModelAdmin):
    list_display = ("currency_code", "currency_name", "currency_symbol")


# Currency rate model
class T01Cur11Admin(admin.ModelAdmin):
    list_display = (
        "convert_curr_from",
        "convert_curr_to",
        "buy_rate_ap",
        "sell_rate_ar",
        "std_rate_gl",
    )


# voucher type
class T01Voc11Inline(admin.TabularInline):
    model = T01Voc11
    fields = (
        "voucher_type",
        "reset_type",
        "voucher_cat",
        "post_option",
        "unpost_option",
        "delete_option",
        "print_header",
        "save_and_print",
    )
    extra = 1


# voucher type parent model
class T01Voc10Admin(T01BaseAdmin):
    inlines = [T01Voc11Inline]
    list_display = (
        "division",
        "prg_type",
        "voucher_type",
        "system_num",
        "voucher_name",
        "subledger_cat",
        "subledger_type",
        "inv_trn_toacc",
        "match_with_gr",
    )
    list_display_links = (
        "division",
        "prg_type",
        "system_num",
        "voucher_name",
        "subledger_cat",
        "subledger_type",
        "inv_trn_toacc",
        "match_with_gr",
    )

    def voucher_type(self, obj):
        return [vou_type.voucher_type for vou_type in obj.voc10.all()]


# Voucher control proxy
class T01VocC10admin(T01Voc10Admin):
    form = T01VocC10Form


admin.site.register(T01VocC10, T01VocC10admin)

# Voucher number setup
class T01Voc12Admin(admin.ModelAdmin):
    list_display = (
        "voucher_type",
        "year_num",
        "period_num",
        "voucher_prefix",
        "starting_num",
        "ending_num",
        "voucher_suffix",
        "next_num",
    )
    readonly_fields = (
        "period_num",
        "pre_audit_close",
        "audit_close",
    )
    actions = ["month_close", "undo_month_close", "check_list_print"]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            return (
                "voucher_type",
                "year_num",
                "starting_num",
                "next_num",
            ) + readonly_fields
        return readonly_fields

    """Month close custom action functionality"""

    @admin.action(description="Month Close")
    def month_close(self, request, queryset):
        closed = 0
        for q in queryset:
            if q.pre_audit_close == False and q.audit_close == False:
                q.lock_flag = True
                q.save()
                closed += 1

        if closed > 0:
            self.message_user(
                request,
                ngettext(
                    "Successfully %d voucher month closed.",
                    "Successfully %d vouchers month closed.",
                    closed,
                )
                % closed,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "Something wrong", messages.ERROR)

    """Undo month close custom action functionality"""

    @admin.action(description="Undo Month Close")
    def undo_month_close(self, request, queryset):
        undo = 0
        for q in queryset:
            if q.pre_audit_close == False and q.audit_close == False:
                q.lock_flag = False
                q.save()
                undo += 1

        if undo > 0:
            self.message_user(
                request,
                ngettext(
                    "Successfully undo %d voucher from month close.",
                    "Successfully undo %d vouchers from month close.",
                    undo,
                )
                % undo,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "Something wrong", messages.ERROR)

    """Check list print custom action functionality"""

    @admin.action(description="Check List Print")
    def check_list_print(self, request, queryset):
        return MonthCloseCheckList().print_pdf(queryset[0])


# Voucher setup proxy
class VoucherTypeListFilter(admin.SimpleListFilter):
    title = _("Voucher Type")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "voucher_type"

    def lookups(self, request, model_admin):
        return (
            (obj.voucher_type, obj)
            for obj in T01Voc11.objects.filter(voucher_name__proxy_code="voc")
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(voucher_type__voucher_type=self.value())


class T01VocC12admin(T01Voc12Admin):
    form = T01VocC12Form
    list_filter = (
        VoucherTypeListFilter,
        "year_num",
        "period_num",
    )


admin.site.register(T01VocC12, T01VocC12admin)

# License Setup
class T01Cfg10Admin(admin.ModelAdmin):
    list_display = ("license_name", "software_name", "status")

    def status(self, obj):
        today = date.today()
        status = ""
        if today > obj.date_expiry:
            status = "License Not Valid"
        return status


# Company Master
class T01Com10Admin(MPTTModelAdmin):
    list_display = (
        "parent",
        "company_name",
        "level",
        "company_address",
        "company_location",
        "logo_file_link",
        "document_header",
        "document_footer",
        "cost_type_co",
        "cost_level_co",
        "active_status",
    )

    actions = ["print_coa_master"]

    """ Print Voucher custom action functionality """

    def print_coa_master(self, request, queryset):
        COMPMaster.get_all_comps()
        pdf_obj = COMPMaster.init_pdf()
        return pdf_obj

    print_coa_master.short_description = "Print Company Master"


# Division
class T01Div10Admin(admin.ModelAdmin):
    list_display = (
        "company",
        "division_name",
        "division_addr",
        "division_location",
        "currency",
        "wps_mol_uid",
        "wps_bank_code",
        "cost_type_div",
        "cost_level_div",
        "checklist_popup",
        "convert_to_caps",
        "invoice_ref_flag",
        "sellprice_flag",
    )
    autocomplete_fields = ("user",)


# Department
class T01Dep10Admin(T01BaseAdmin):
    list_display = (
        "division",
        "department_code",
        "department_name",
    )


# Designation
class T01Dsg10Admin(T01BaseAdmin):
    list_display = (
        "department",
        "designation",
        "trade_category",
        "payroll_group",
        "attendance_type",
        "weekend_days",
        "average_daily_cost",
        "hours_for_OT",
    )
    readonly_fields = ["average_daily_cost"]


# Warehouse Master
class T01Whm10Admin(T01BaseAdmin):
    list_display = (
        "division",
        "warehouse_code",
        "warehouse_name",
        "batch_flag",
        "goods_return_recost",
        "additional_cost_to_inventory",
        "post_inventory_to_acct",
        "cost_type_wh",
        "cost_level_wh",
    )


# Project Master
class T01Prj10Admin(T01BaseAdmin):
    list_display = (
        "project_code",
        "project_name",
        "project_number",
        "division",
        "project_subLedger",
        "project_address",
        "estimated_value",
        "actual_value",
        "project_status",
        "project_COA",
        "project_WH",
    )
    readonly_fields = ["actual_value"]


# Setup Auto email
class T01Atm10Admin(admin.ModelAdmin):
    list_display = (
        "email_code",
        "report_name",
        "mail_from",
        "mail_to",
        "subject",
        "message",
    )


# UoM Master
class T01Uom10Admin(admin.ModelAdmin):
    list_display = ("unit_of_measure", "measure_type", "unit_desc")


# UoM Conversion
class T01Uom11Admin(admin.ModelAdmin):
    list_display = ("unit_from", "unit_to", "conversion_rate")


# # Unit Classification
# class T01Uom20Admin(admin.ModelAdmin):
#     list_display = ('measure_type', 'measure_name')

# Nationality Master
class T01Nat10Admin(admin.ModelAdmin):
    list_display = ("nationality",)


admin.site.register(T01Cat10, T01Cat10Admin)
admin.site.register(T01Cur10, T01Cur10Admin)
admin.site.register(T01Cur11, T01Cur11Admin)
admin.site.register(T01Cfg10, T01Cfg10Admin)
admin.site.register(T01Com10, T01Com10Admin)
admin.site.register(T01Div10, T01Div10Admin)
admin.site.register(T01Dep10, T01Dep10Admin)
admin.site.register(T01Dsg10, T01Dsg10Admin)
admin.site.register(T01Whm10, T01Whm10Admin)
admin.site.register(T01Prj10, T01Prj10Admin)
admin.site.register(T01Atm10, T01Atm10Admin)
admin.site.register(T01Uom10, T01Uom10Admin)
admin.site.register(T01Uom11, T01Uom11Admin)
admin.site.register(T01Nat10, T01Nat10Admin)
admin.site.register([T01Slu10])
