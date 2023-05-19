from django.contrib import admin, messages

from ebos2206.models.m06_hr_trn import *
from ebos2206.utils.u06_hr_trn import EOSExport, WPSExport


class T06Wps11Inline(admin.TabularInline):
    model = T06Wps11

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + (
                "wps_header",
                "emp_record_type",
                "emp_prl_id",
                "emp_UID",
                "emp_name",
                "emp_bnk_id",
                "emp_Bnk_acct",
                "sal_fixed_amt",
                "sal_Variable_amt",
                "emp_lve_days",
                "emp_housing_alw",
                "emp_transport_alw",
                "emp_tkt_amt",
                "emp_ot_amt",
                "emp_other_alw",
                "emp_lve_encashment",
                "emp_medical_alw",
            )
        return self.readonly_fields


class T06Wps10Admin(admin.ModelAdmin):
    inlines = [T06Wps11Inline]
    list_display = (
        "wps_year",
        "wps_month",
        "division",
        "com_record_type",
        "com_UID",
        "com_bnk_name",
        "com_bnk_routing_code",
        "com_ref_note",
        "sif_file_name",
    )
    readonly_fields = ("sif_file_name",)
    actions = ["export_wps_csv"]

    def export_wps_csv(self, request, queryset):

        for obj in queryset:
            WPSExport().wps_csv_data(obj)
        return messages.success(request, "WPS file downloaded successfully !")

    export_wps_csv.short_description = "WPS file download"


admin.site.register(T06Wps10, T06Wps10Admin)


class T06Eos10Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "gratuity_note",
        "gratuity_amount",
        "el_days",
        "el_note",
        "el_amount",
        "loan_balance_amount",
        "ticket_amount",
        "pending_pay",
        "pending_deduction",
        "eos_note",
        "post_flag",
        "print_EOS",
    )
    readonly_fields = ["print_EOS"]
    actions = ["print_eos_form"]

    def print_eos_form(self, request, queryset):
        for obj in queryset:
            EOSExport().eos_pdf_data(obj)
        return messages.success(request, "EOS form report updated successfully")

    print_eos_form.short_description = "Print EOS form"


# Self Service Expense Claim
class T06Ess02Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "claim_cat",
        "claim_date",
        "claim_note",
        "claim_amount",
        "claim_status",
        "claim_approver",
        "approver_note",
        "date_approved",
        "bill_copy",
    )
    readonly_fields = (
        "employee_code",
        "gl_code",
        "claim_status",
        "claim_approver",
        "approver_note",
        "date_approved",
    )

    # Filter record on basis of user id (employee code)
    def save_model(self, request, obj, form, change):
        user_id = request.user
        get_employee = T06Emp10.objects.filter(employee_code=user_id).first()
        if get_employee:
            get_employee = T06Emp10.objects.get(employee_code=user_id)
            obj.employee_code = get_employee
        super().save_model(request, obj, form, change)

    # list record on basis of logged In username equals employee code
    def get_queryset(self, request):
        user_id = request.user
        check_superuser = user_id.is_superuser
        try:
            if check_superuser != True:
                get_employee = T06Emp10.objects.get(employee_code=user_id)
                get_records = T06Exc10.objects.filter(employee_code=get_employee)
            else:
                get_records = T06Exc10.objects.all()
            return get_records
        except Exception as error:
            return str(error)

    # make fields readonly when specific conditions met
    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.date_approved:
                return self.readonly_fields + tuple(
                    [item.name for item in obj._meta.fields]
                )
        return self.readonly_fields


# Self Services Help Desk
class T06Ess03Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "service_request",
        "dt_of_request",
        "service_status",
        "service_due_date",
        "service_note",
        "serviced_by",
    )
    readonly_fields = (
        "employee_code",
        "service_status",
        "service_due_date",
        "service_note",
        "serviced_by",
    )

    # auto update employee code when employee add record
    def save_model(self, request, obj, form, change):
        user_id = request.user
        get_employee = T06Emp10.objects.filter(employee_code=user_id).first()
        if get_employee:
            get_employee = T06Emp10.objects.get(employee_code=user_id)
            obj.employee_code = get_employee
        super().save_model(request, obj, form, change)

    # list record on basis of logged In username equals employee code
    def get_queryset(self, request):
        user_id = request.user
        check_superuser = user_id.is_superuser
        try:
            if check_superuser != True:
                get_employee = T06Emp10.objects.get(employee_code=user_id)
                get_records = T06Ess03.objects.filter(employee_code=get_employee)
            else:
                get_records = T06Ess03.objects.all()
            return get_records
        except Exception as error:
            return str(error)


# Self Service Memo
class T06Ess04Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "memo_ref_no",
        "memo_type",
        "memo_count",
        "memo_text",
        "issued_by",
        "authorized_by",
        "acknowledged",
        "feedback",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    # list record on basis of logged In username equals employee code
    def get_queryset(self, request):
        user_id = request.user
        check_superuser = user_id.is_superuser
        try:
            if check_superuser != True:
                get_employee = T06Emp10.objects.get(employee_code=user_id)
                get_records = T06Ess04.objects.filter(employee_code=get_employee)
            else:
                get_records = T06Ess04.objects.all()
            return get_records
        except Exception as error:
            return str(error)


class T06Exc10Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "claim_cat",
        "gl_code",
        "claim_date",
        "claim_note",
        "claim_amount",
        "claim_status",
        "claim_approver",
        "approver_note",
        "date_approved",
        "bill_copy",
    )


class T06Hdt10Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "service_request",
        "dt_of_request",
        "service_status",
        "service_due_date",
        "service_note",
        "serviced_by",
    )


class TT06Mem10Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "memo_ref_no",
        "memo_type",
        "memo_count",
        "memo_text",
        "issued_by",
        "authorized_by",
        "acknowledged",
        "feedback",
    )


admin.site.register(T06Eos10, T06Eos10Admin)
admin.site.register(T06Ess02, T06Ess02Admin)
admin.site.register(T06Ess03, T06Ess03Admin)
admin.site.register(T06Ess04, T06Ess04Admin)
admin.site.register(T06Exc10, T06Exc10Admin)
admin.site.register(T06Hdt10, T06Hdt10Admin)
admin.site.register(T06Mem10, TT06Mem10Admin)
