import csv
import io

from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from ebos2201.models.m01_fin_mas import *
from ebos2206.models.m06_att_trn import *
from ebos2206.models.m06_prl_trn import *


@admin.register(T06Tam10)
class T06Tam10Admin(admin.ModelAdmin):
    list_display = ["employee_code", "payroll_period", "attendance_date", "time_in", "time_out", "weekend_flag", "public_holiday_flag", "lock_flag"]


@admin.register(T06Tbd10)
class T06Tbd10Admin(admin.ModelAdmin):
    list_display = ["employee_code", "payroll_period", "att_date", "normal_work_hrs", "normal_OT_hrs", "weekend_OT_hrs", "holiday_OT_hrs", "lock_flag"]


@admin.register(T06Tbm10)
class T06Tbm10Admin(admin.ModelAdmin):
    list_display = ["employee_code", "payroll_period", "normal_work_days", "normal_OT_hrs", "total_weekend_days", "total_public_holidays", "total_unpaid_weekend_days", "total_unpaid_public_holidays", "lock_flag"]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


admin.site.register(T06Phd10)

@admin.register(T06Prs10)
class T06Prs10Admin(admin.ModelAdmin):
    list_display = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "att_lock_flag",
        "prl_lock_flag",
        "prl_run_flag",
        "prl_post_flag",
        "pmt_post_flag"
    )
    
    # def has_add_permission(self, request) -> bool:
    #     return False

    # def has_change_permission(self, request, obj=None) -> bool:
    #     return False

    # def has_delete_permission(self, request, obj=None) -> bool:
    #     return False


class T06Atd10Admin(admin.ModelAdmin):
    list_display = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "att_lock_flag",
        "attn_machine_file",
        "daily_attn_file",
    )
    readonly_fields = ("att_lock_flag",)
    exclude = (
        "prg_type",
        "payroll_checklist",
        "payslip",
        "prl_lock_flag",
        "prl_post_flag",
        "pmt_post_flag",
        "prl_run_flag",
    )
    actions = [
        "import_att_mchn_data",
        "import_daily_att_log",
        "download_monthly_att",
        "download_daily_att",
    ]

    def import_att_mchn_data(self, request, queryset):
        from datetime import datetime

        for obj in queryset:
            if obj.att_lock_flag == False:
                if file := obj.attn_machine_file:
                    data_set = file.read().decode("UTF-8")
                    io_string = io.StringIO(data_set)
                    next(io_string)
                    for column in csv.reader(io_string, delimiter=","):
                        if column[4]:
                            attendance_date = datetime.strptime(column[4], "%Y-%m-%d")
                            year = attendance_date.year
                            month = attendance_date.month
                            attendance_day = attendance_date.weekday()
                        else:
                            attendance_date, year, month, attendance_day = None, None, None, None

                        try:
                            employee_code = T06Emp10.objects.get(employee_code=column[0])
                        except ObjectDoesNotExist:
                            employee_code = None

                        if column[3]:
                            try:
                                project_id = T01Prj10.objects.get(id=column[3]).id
                            except ObjectDoesNotExist:
                                project_id = None
                        else:
                            project_id = None

                        try:
                            payroll_period = T06Prs10.objects.get(
                                pay_year=year,
                                pay_month=month,
                                division=column[1],
                                payroll_group=column[2],
                            )
                        except ObjectDoesNotExist:
                            raise ValidationError(
                                {"detail": "The payroll period are not match with uploaded file."}
                            )
                        
                        # Create Record in T06Tam10 from csv file
                        T06Tam10.objects.create(
                            employee_code=employee_code,
                            payroll_period=payroll_period,
                            attendance_date=attendance_date,
                            attendance_day=attendance_day,
                            project_id=project_id,
                            time_in=column[5] if column[5] else None,
                            entry_code=column[6] if column[6] else None,
                            time_out=column[7] if column[7] else None,
                            exit_code=column[8] if column[8] else None,
                            weekend_flag=column[9] if column[9] else None,
                            public_holiday_flag=column[10] if column[10] else None,
                            transaction_type=column[11] if column[11] else None,
                            attendance_note=column[12] if column[12] else None,
                        )

                    T06Tbd10.get_TAM_data(obj)
                    T06Tbm10.read_TBD_log(obj)
                    T06Atd10.objects.filter(id=obj.id).update(att_lock_flag=True)

                    # Update the attendace data lock
                    T06Tam10.objects.filter(
                        payroll_period=obj, lock_flag=False
                    ).update(lock_flag=True)
                    T06Tbd10.objects.filter(
                        payroll_period=obj, lock_flag=False
                    ).update(lock_flag=True)
                    T06Tbm10.objects.filter(
                        payroll_period=obj, lock_flag=False
                    ).update(lock_flag=True)

                    self.message_user(
                        request, "Data Imported Successfully!", messages.SUCCESS
                    )
                else:
                    self.message_user(
                        request, "No file found.", messages.ERROR
                    )
            else:
                self.message_user(
                    request, "Attendance Lock Flag is True.", messages.WARNING
                )

    import_att_mchn_data.short_description = "Import attendance machine data"

    def import_daily_att_log(self, request, queryset):
        for obj in queryset:
            if obj.att_lock_flag == False:
                get_T06Tam10 = T06Tam10.objects.filter(payroll_period=obj.id)
                if not get_T06Tam10:
                    if file := obj.daily_attn_file:                    
                        data_set = file.read().decode("UTF-8")
                        io_string = io.StringIO(data_set)
                        next(io_string)
                        for column in csv.reader(io_string, delimiter=","):
                            try:
                                employee_code = T06Emp10.objects.get(
                                    employee_code=column[1]
                                )
                            except ObjectDoesNotExist:
                                employee_code = None
                            try:
                                payroll_period = T06Prs10.objects.get(pay_year=column[2])
                            except ObjectDoesNotExist:
                                payroll_period = None
                            try:
                                project_code = T01Prj10.objects.get(project_code=column[5])
                            except ObjectDoesNotExist:
                                project_code = None

                            # Create Records in T06Tbd10
                            T06Tbd10.objects.create(
                                employee_code=employee_code,
                                payroll_period=payroll_period,
                                att_date=column[3] if column[3] else None,
                                att_day=column[4] if column[4] else None,
                                project=project_code,
                                normal_work_hrs=column[6] if column[6] else None,
                                normal_OT_hrs=column[7] if column[7] else None,
                                weekend_OT_hrs=column[8] if column[8] else None,
                                holiday_OT_hrs=column[9] if column[9] else None,
                                weekend_flag=column[10] if column[10] else None,
                                public_holiday_flag=column[11] if column[11] else None,
                                paid_weekend=column[12] if column[12] else None,
                                paid_public_holiday=column[13] if column[13] else None,
                                lock_flag=column[14] if column[14] else None,
                            )

                        # T06Tbm10.read_TBD_log(obj.pay_month, obj.pay_year)
                    T06Atd10.objects.filter(id=obj.id).update(att_lock_flag=True)

                    # Update the attendace data lock
                    T06Tam10.objects.filter(
                        payroll_period=obj, lock_flag=False
                    ).update(lock_flag=True)
                    T06Tbd10.objects.filter(
                        payroll_period=obj, lock_flag=False
                    ).update(lock_flag=True)
                    T06Tbm10.objects.filter(
                        payroll_period=obj, lock_flag=False
                    ).update(lock_flag=True)

                    self.message_user(
                        request, "Data Imported Successfully!", messages.SUCCESS
                    )
                else:
                    self.message_user(
                        request, "No file found.", messages.ERROR
                    )
            else:
                self.message_user(
                    request, "Attendance Lock Flag is True.", messages.WARNING
                )

    import_daily_att_log.short_description = "Import daily attendance log"

    def download_monthly_att(self, request, queryset):
        for obj in queryset:
            if queryset.count() != 1:
                self.message_user(
                    request,
                    "Can not download more than one record to csv at once.",
                    messages.ERROR,
                )
                return
            else:
                T06Tbd10_meta = T06Tbd10._meta
                field_names = [field.name for field in T06Tbd10_meta.fields]
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = "attachment; filename={}.csv".format(
                    T06Tbd10_meta
                )
                writer = csv.writer(response)
                writer.writerow(field_names)
                T06Tbd10_records = T06Tbd10.objects.filter(payroll_period=obj.id)
                for T06Tbd10_records in T06Tbd10_records:
                    row = writer.writerow(
                        [getattr(T06Tbd10_records, field) for field in field_names]
                    )
                return response

    download_monthly_att.short_description = "Download Monthly attendance data"

    def download_daily_att(self, request, queryset):
        for obj in queryset:
            if queryset.count() != 1:
                self.message_user(
                    request,
                    "Can not download more than one record to csv at once.",
                    messages.ERROR,
                )
                return
            else:
                T06Tbm10_meta = T06Tbm10._meta
                field_names = [field.name for field in T06Tbm10_meta.fields]
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = "attachment; filename={}.csv".format(
                    T06Tbm10_meta
                )
                writer = csv.writer(response)
                writer.writerow(field_names)
                T06Tbm10_records = T06Tbm10.objects.filter(payroll_period=obj.id)
                for T06Tbm10_records in T06Tbm10_records:
                    row = writer.writerow(
                        [getattr(T06Tbm10_records, field) for field in field_names]
                    )
                return response

    download_daily_att.short_description = "Download daily attendance data"

    # def delete_queryset(self, request, queryset):
    #     for obj in queryset:
    #         if obj.prl_lock_flag == False:
    #             print(obj.prl_lock_flag)
    #             get_T06Tam10 = T06Tam10.objects.filter(payroll_period=obj.id)
    #             get_T06Tam10.delete()
    #             get_T06Tbd10 = T06Tbd10.objects.filter(payroll_period=obj.id)
    #             get_T06Tbd10.delete()
    #             get_T06Tbm10 = T06Tbm10.objects.filter(payroll_period=obj.id)
    #             get_T06Tbm10.delete()
    #     T06Atd10.objects.filter(id=obj.id).update(att_lock_flag=False)


admin.site.register(T06Atd10, T06Atd10Admin)


class T06Pay10Admin(admin.ModelAdmin):
    list_display = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "att_lock_flag",
        "prl_lock_flag",
        "prl_run_flag",
        "prl_post_flag",
        "pmt_post_flag",
        "payroll_checklist",
    )
    exclude = (
        "prg_type",
        "attn_machine_file",
        "daily_attn_file",
    )
    readonly_fields = (
        "att_lock_flag",
        "prl_lock_flag",
        "prl_post_flag",
        "pmt_post_flag",
        "payroll_checklist",
        "payslip",
    )
    actions = ["process_payroll", "update_payroll_amount"]

    def process_payroll(self, request, queryset):

        for obj in queryset:
            if not obj.prl_post_flag:
                if obj.att_lock_flag:
                    if not obj.prl_run_flag:
                        if not obj.prl_lock_flag:
                            T06Prl10.get_monthly_att(obj)
                            T06Prl12.insert_t06prl12(obj)
                            T06Prl13.insert_t06prl13(obj)
                            T06Prl14.insert_t06prl14(obj)
                            T06Prl15.insert_t06prl15(obj)
                            T06Prl16.insert_t06prl16(obj)
                            T06Prl10.update_monthly_att(obj)
                            T06Prl12.update_t06prl12(obj)
                            T06Prl12.update_t06emp12(obj)
                            T06Prl11.insert_t06prl11(obj)

                            T06Prs10.objects.filter(id=obj.id).update(prl_run_flag=True)
                            self.message_user(
                                request, "The payroll process successed.", messages.SUCCESS
                            )  
                        else:
                            self.message_user(
                                request, "The payroll process already locked.", messages.WARNING
                            )        
                    else:
                        self.message_user(
                            request, "Payroll already processed.", messages.WARNING
                        )
                else:
                    self.message_user(
                        request, "Attendance data should be locked for this period.", messages.WARNING
                    )
            else:
                self.message_user(
                    request, "The payroll post flag is True.", messages.WARNING
                )

    process_payroll.short_description = "Process Payroll"

    def update_payroll_amount(self, request, queryset):

        for obj in queryset:
            if not obj.prl_post_flag:
                if obj.att_lock_flag:
                    if not obj.prl_run_flag:
                        if not obj.prl_lock_flag:
                            # Update payroll amount
                            T06Prl14.update_t06prl14(obj)
                            T06Prl15.update_t06prl15(obj)
                            T06Prl16.update_t06prl16(obj)
                            T06Prl11.update_t06prl11(obj)

                            T06Prs10.objects.filter(id=obj.id).update(prl_lock_flag=True)
                            self.message_user(
                                request, "The payroll amount was successfully updated.", messages.SUCCESS
                            )  
                        else:
                            self.message_user(
                                request, "The payroll process already locked.", messages.WARNING
                            )        
                    else:
                        self.message_user(
                            request, "Payroll already processed.", messages.WARNING
                        )
                else:
                    self.message_user(
                        request, "Attendance data should be locked for this period.", messages.WARNING
                    )
            else:
                self.message_user(
                    request, "The payroll post flag is True.", messages.WARNING
                )

    update_payroll_amount.short_description = "Update Payroll Amount"


class T06Pst10Admin(T06Prs10Admin):
    list_display = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "att_lock_flag",
        "prl_lock_flag",
        "prl_post_flag",
        "pmt_post_flag",
        "attn_machine_file",
        "daily_attn_file",
    )
    exclude = ("prg_type",)
    actions = ["post_payroll"]

    def post_payroll(self, request, queryset):
        for obj in queryset:
            payroll_period_per_year = obj.pay_year
            payroll_period_pay_month = obj.pay_month
            payroll_period = T06Prs10.objects.filter(
                pay_year=payroll_period_per_year, pay_month=payroll_period_pay_month
            )
            data_check = T06Prl10.objects.filter(
                employee_code__designation__department__division=obj.division,
                employee_code__designation__payroll_group=obj.payroll_group,
                payroll_period__pay_year=payroll_period_per_year,
                payroll_period__pay_month=payroll_period_pay_month,
            )
            # if data_check and obj.prl_post_flag == False:
            #     vocher_number = T01Glc10.auto_gl_post(T06Prl10.gl_code,  T06Emp10.sub_ledger)
            # T06Prl10.gl_voucher = vocher_number
            # T06Prs10.prl_post_flag = True

    post_payroll.short_description = "Post Payroll"


class T06Ups10Admin(T06Prs10Admin):
    list_display = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "att_lock_flag",
        "prl_lock_flag",
        "prl_post_flag",
        "pmt_post_flag",
        "attn_machine_file",
        "daily_attn_file",
    )
    exclude = ("prg_type",)
    actions = ["post_payroll"]

    def post_payroll(self, request, queryset):
        for obj in queryset:
            payroll_period_per_year = obj.pay_year
            payroll_period_pay_month = obj.pay_month
            payroll_period = T06Prs10.objects.filter(
                pay_year=payroll_period_per_year, pay_month=payroll_period_pay_month
            )
            data_check = T06Prl10.objects.filter(
                employee_code__designation__department__division=obj.division,
                employee_code__designation_payroll_group=obj.payroll_group,
                payroll_period__pay_year=payroll_period_per_year,
                payroll_period__pay_month=payroll_period_pay_month,
            )
            # if data_check and (T06Prs10.objects.filter().first().prl_post_flag == True):
            #     T01Glc10.auto_gl_unpost(T06Prl10.gl_voucher)
            #     T06Prl10.gl_voucher = 0
            #     T06Prs10.prl_post_flag = False

    post_payroll.short_description = "Payroll Unposting"


@admin.register(T06Lve10)
class T06Lve10Admin(admin.ModelAdmin):
    list_display = [        
        'employee_code', 
        'leave_code', 
        'request_type', 
        'request_date_from', 
        'request_date_to', 
        'request_note', 
        'user_approved', 
        'dt_of_approval', 
        'leave_status',
    ]


class T06Hrr01Admin(T06Prs10Admin):
    list_display = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "payroll_checklist",
    )
    exclude = ("prg_type",)


class T06Hrr02Admin(T06Prs10Admin):
    list_display = ("division", "pay_year", "pay_month", "payroll_group", "payslip")
    exclude = ("prg_type",)


class T06Ess01Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "leave_code",
        "leave_status",
        "request_type",
        "request_date_from",
        "request_date_to",
        "request_note",
        "user_approved",
        "dt_of_approval",
        "approver_note",
        "approved_from_date",
        "approved_to_date",
        "actual_date_from",
        "actual_date_to",
    )
    readonly_fields = (
        "employee_code",
        "leave_status",
        "user_approved",
        "dt_of_approval",
        "approver_note",
        "approved_from_date",
        "approved_to_date",
        "actual_date_from",
        "actual_date_to",
    )

    def save_model(self, request, obj, form, change):
        user_id = request.user
        get_employee = T06Emp10.objects.filter(employee_code=user_id).first()
        if get_employee:
            get_employee = T06Emp10.objects.get(employee_code=user_id)
            obj.employee_code = get_employee
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        user_id = request.user
        check_superuser = user_id.is_superuser
        try:
            if check_superuser != True:
                get_employee = T06Emp10.objects.get(employee_code=user_id)
                get_records = T06Lve10.objects.filter(employee_code=get_employee)
            else:
                get_records = T06Lve10.objects.all()
            return get_records
        except Exception as error:
            return "No Matching records found!"

    # make fields readonly when specific conditions met
    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.approved_from_date:
                return self.readonly_fields + tuple(
                    [item.name for item in obj._meta.fields]
                )
        return self.readonly_fields


class T06Ess05Admin(admin.ModelAdmin):
    list_display = ("division", "pay_year", "pay_month", "payroll_group", "payslip")
    exclude = ("prg_type",)
    readonly_fields = (
        "division",
        "pay_year",
        "pay_month",
        "payroll_group",
        "att_lock_flag",
        "prl_lock_flag",
        "prl_post_flag",
        "pmt_post_flag",
        "attn_machine_file",
        "daily_attn_file",
        "payroll_checklist",
        "payslip",
    )    

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def get_queryset(self, request):
        user_id = request.user
        check_superuser = user_id.is_superuser
        try:
            if check_superuser != True:
                get_employee = T06Emp10.objects.get(employee_code=user_id)
                get_records = T06Ess05.objects.filter(employee_code=get_employee)
            else:
                get_records = T06Ess05.objects.all()
            return get_records
        except Exception as error:
            return str(error)


class T06Ess06Admin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "project",
        "normal_work_days",
        "normal_OT_hrs",
        "holiday_OT_hrs",
        "weekend_OT_hrs",
        "total_weekend_days",
        "total_public_holidays",
        "total_unpaid_weekend_days",
        "total_unpaid_public_holidays"
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def get_queryset(self, request):
        user_id = request.user
        check_superuser = user_id.is_superuser
        try:
            if check_superuser != True:
                get_employee = T06Emp10.objects.get(employee_code=user_id)
                get_records = T06Ess06.objects.filter(employee_code=get_employee)
            else:
                get_records = T06Ess06.objects.all()
            return get_records
        except Exception as error:
            return str(error)


admin.site.register(T06Pay10, T06Pay10Admin)
admin.site.register(T06Pst10, T06Pst10Admin)
admin.site.register(T06Ups10, T06Ups10Admin)
admin.site.register(T06Hrr01, T06Hrr01Admin)
admin.site.register(T06Hrr02, T06Hrr02Admin)
admin.site.register(T06Ess01, T06Ess01Admin)
admin.site.register(T06Ess05, T06Ess05Admin)
admin.site.register(T06Ess06, T06Ess06Admin)
