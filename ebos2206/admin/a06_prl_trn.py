from django.contrib import admin

from ebos2206.models.m06_prl_trn import *


class T06Prl11Inline(admin.TabularInline):
    model = T06Prl11
    readonly_fields = (
        "project",
        "prj_work_days",
        "prj_ot_hours",
        "prj_allowance",
        "prj_labour_cost",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T06Prl12Inline(admin.TabularInline):
    model = T06Prl12
    readonly_fields = (
        "leave_code",
        "leave_days",
        "leave_pay_days",
        "leave_pay_amount",
        "encash_days",
        "encash_amount",
        "accrued_days",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T06Prl13Inline(admin.TabularInline):
    model = T06Prl13
    readonly_fields = (
        "employee_allowances",
        "alw_unit_qty",
        "project",
        "project_alw_amt",
        "wps_housing_amt",
        "wps_transport_amt",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T06Prl14Inline(admin.TabularInline):
    model = T06Prl14
    readonly_fields = (
        "ticket_rule",
        "ticket_paid_amount",
        "encash_amount",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T06Prl15Inline(admin.TabularInline):
    model = T06Prl15
    readonly_fields = (
        "loan_availed",
        "loan_emi",
        "payroll_rundt",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T06Prl16Inline(admin.TabularInline):
    model = T06Prl16
    readonly_fields = ("monthly_deduction",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T06Prl10Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "payroll_period",
        "basic_pay",
        "leavepay_provision",
        "ot_pay",
        "ml_pay",
        "el_pay",
        "other_pay",
        "tkt_pay",
        "wps_housing_amt",
        "wps_transport_amt",
        "variable_alw",
        "deductions",
        "loan_emi",
        "round_off",
    )
    list_filter = (
        "employee_code__first_name",
        "employee_code__last_name",
        "basic_pay",
    )
    search_fields = (
        "employee_code__first_name",
        "employee_code__last_name",
        "basic_pay",
    )
    readonly_fields = (
        "employee_code",
        "payroll_period",
        "tot_days_worked",
        "tot_ot_hours",
        "tot_ML_days",
        "tot_EL_days",
        "tot_LOP_days",
        "gratuity_provision",
        "ticket_provision",
        "leavepay_provision",
        "basic_pay",
        "ot_pay",
        "ml_pay",
        "el_pay",
        "other_pay",
        "tkt_pay",
        "fixed_alw",
        "variable_alw",
        "deductions",
        "loan_emi",
        "round_off",
        "gl_code",
        "gl_voucher",
        "wps_housing_amt",
        "wps_transport_amt",
    )

    inlines = [
        T06Prl11Inline,
        T06Prl12Inline,
        T06Prl13Inline,
        T06Prl14Inline,
        T06Prl15Inline,
        T06Prl16Inline,
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(T06Prl10, T06Prl10Admin)
