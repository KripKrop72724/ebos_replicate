from django.contrib import admin, messages

from ebos2201.notification import send_email
from ebos2206.models.m06_emp_mas import *


class T06Emp11Inline(admin.TabularInline):
    model = T06Emp11
    fields = (
        "bank_name",
        "beneficiery",
        "bank_acc",
        "bank_iban",
        "bank_swift_code",
        "active_flag",
    )


class T06Emp12Inline(admin.TabularInline):
    model = T06Emp12
    fields = (
        "leave_code",
        "leave_opbal_date",
        "leave_opbal",
        "leave_accrual",
        "leave_availed",
        "leave_encashed",
        "leave_clbal",
        "leave_clbal_date",
    )


class T06Emp13Inline(admin.TabularInline):
    model = T06Emp13
    fields = (
        "allowance_code",
        "allowance_rate",
        "allowance_unit",
        "wps_housing",
        "wps_transport",
    )


class T06Emp14Inline(admin.TabularInline):
    model = T06Emp14
    fields = (
        "ticket_rule",
        "home_country",
        "ticket_count",
        "ticket_amount",
    )


class T06Emp15Inline(admin.TabularInline):
    model = T06Emp15
    fields = (
        "loan_type",
        "loan_amount",
        "no_of_emi",
        "emi_amount",
        "last_emi_adjustment",
        "total_loan_deduction",
        "net_loan_balance",
        "deduction_start_date",
        "deduction_asof_date",
        "loan_ref",
    )


class T06Emp16Inline(admin.TabularInline):
    model = T06Emp16
    fields = (
        "deduction_code",
        "deduction_amount",
    )


class T06Emp17Inline(admin.TabularInline):
    model = T06Emp17
    fields = (
        "asset_ref",
        "dt_of_issue",
        "dt_of_return",
    )


class T06Emp18Inline(admin.TabularInline):
    model = T06Emp18
    fields = (
        "document_name",
        "attachment",
        "document_no",
        "dt_of_issue",
        "dt_of_expiry",
        "place_of_issue",
        "ref1",
        "ref2",
    )


class T06Emp10Admin(admin.ModelAdmin):
    list_display = [
        "employee_code",
        "first_name",
        "last_name",
        "designation",
        "mobile",
        "email",
        "employee_status",
    ]
    inlines = [
        T06Emp11Inline,
        T06Emp12Inline,
        T06Emp13Inline,
        T06Emp14Inline,
        T06Emp15Inline,
        T06Emp16Inline,
        T06Emp17Inline,
        T06Emp18Inline,
    ]


class T06Dex10Admin(admin.ModelAdmin):
    list_display = (
        "division",
        "department",
        "document_type",
        "date_from",
        "date_to",
        "report_file",
        "email_code",
    )
    readonly_fields = ("report_file",)
    actions = ["send_email"]

    def send_email(self, request, queryset):
        success_email = []
        error_email = []
        for obj in queryset:
            try:
                subject = "Testing"
                message = "Here is the Report for Document Renewel."
                recipient_list = [
                    obj.email_code.mail_to,
                ]
                send_email(
                    subject, message, recipient_list, attachement=obj.report_file.path
                )
                success_email.append(obj)
            except Exception as e:
                print("error", str(e))
                error_email.append(obj)
                response = messages.error(request, str(e))
        if success_email:
            response = messages.success(
                request, "" + str(len(success_email)) + " Email Sent Successfully "
            )
        return response


admin.site.register(T06Emp10, T06Emp10Admin)
admin.site.register(T06Dex10, T06Dex10Admin)
admin.site.register([T06Emp18])
