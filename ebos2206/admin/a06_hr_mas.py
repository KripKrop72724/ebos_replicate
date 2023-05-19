from django.contrib import admin

from ebos2206.models.m06_hr_mas import *


@admin.register(T06Cfg10)
class T06Cfg10Admin(admin.ModelAdmin):
    list_display = (
        "division",
        "net_roundoff",
        "max_working_hrs",
        "add_EL_ML_for_netpay",
        "pay_perday_div",
    )


@admin.register(T06Alw10)
class T06Alw10Admin(admin.ModelAdmin):
    list_display = (
        "allowance_name",
        "allowance_code",
        "allowance_type",
        "as_per_days_worked",
        "variable_amount_per_mnt",
    )


@admin.register(T06Ded10)
class T06Ded10Admin(admin.ModelAdmin):
    list_display = (
        "deduction_name",
        "deduction_code",
        "gl_code",
    )


@admin.register(T06Lon10)
class T06Lon10Admin(admin.ModelAdmin):
    list_display = (
        "loan_type",
        "loan_code",
        "gl_code",
    )


@admin.register(T06Doc10)
class T06Doc10Admin(admin.ModelAdmin):
    list_display = (
        "document_name",
    )


@admin.register(T06Lvr10)
class T06Lvr10Admin(admin.ModelAdmin):
    list_display = (
        "division",
        "leave_code",
        "leave_name",
        "days_allowed",
        "days_eligible",
        "days_with_pay",
        "carryfwd_leave",
        "encash_leave",
    )


@admin.register(T06Tkr10)
class T06Tkr10Admin(admin.ModelAdmin):
    list_display = (
        "department",
        "ticket_cycle",
        "ticket_ratio",
        "encash_ticket",
        "gl_code",
    )
