import logging
import sys
from calendar import monthrange

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2201.utils import get_no_of_days
from ebos2201.validators import validate_month, validate_year
from ebos2206.models.m06_emp_mas import T06Emp10, T06Emp12
from ebos2206.validators import validate_file_extension

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Payroll Run Setup
class T06Prs10(models.Model):
    prg_type = models.CharField(
        max_length=6, null=True, blank=True, db_column="sPrgType"
    )
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column="IDDivPRS")
    pay_year = models.PositiveIntegerField(
        db_column="nPayYear", validators=validate_year()
    )
    pay_month = models.PositiveIntegerField(
        db_column="nPayMonth", validators=validate_month()
    )
    payroll_group = models.ForeignKey(
        T01Cat10,
        models.PROTECT,
        db_column="sPrsGroup",
        blank=True,
        null=True,
        limit_choices_to={"program_code": "T06Prs10"},
    )
    att_lock_flag = models.BooleanField(db_column="bAttLock", default=False)
    prl_lock_flag = models.BooleanField(db_column="bPrlLock", default=False)
    prl_run_flag = models.BooleanField(db_column="bPrlRun", default=False)
    prl_post_flag = models.BooleanField(db_column="bPrlPostLock", default=False)
    pmt_post_flag = models.BooleanField(db_column="bPmtPostLock", default=False)
    attn_machine_file = models.FileField(
        upload_to="payroll_csv",
        validators=[validate_file_extension],
        null=True,
        db_column="flatmc",
        blank=True,
    )
    daily_attn_file = models.FileField(
        upload_to="payroll_csv",
        null=True,
        db_column="fldat",
        blank=True,
        validators=[validate_file_extension],
    )
    payroll_checklist = models.FileField(
        upload_to="payroll_reports", null=True, db_column="flprchk", blank=True
    )
    payslip = models.FileField(
        upload_to="payslips", null=True, db_column="flpysl", blank=True
    )

    class Meta:
        db_table = "T06PRS10"
        verbose_name = "Payroll Run"
        verbose_name_plural = "Payroll Run"
        # unique_together = ('pay_year', 'pay_month')
        ordering = ("pay_year",)

    @property
    def machine_data(self):
        return self.machine_period_set.all()

    @property
    def daily_data(self):
        return self.daily_period_set.all()

    def __str__(self) -> str:
        return f"{self.id} - {self.pay_year} - {self.pay_month}"

    def insert_payroll(month, year):
        return T06Prs10.objects.create(pay_year=year, pay_month=month)

    def auto_gl_post(self):
        self.prl_post_flag = True
        self.save()

    def auto_gl_unpost(self):
        self.prl_post_flag = False
        self.save()


# Proxy of T06Prs10 for Attendance Data
class T06Atd10(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "b1.Attendance Data"


# Proxy of T06Prs10 for Payroll Process
class T06Pay10(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "b5.Payroll Process"


# Proxy of T06Prs10 for Payroll Posting
class T06Pst10(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "b7.Payroll Posting"


# Proxy of T06Prs10 for Payroll Unsposting
class T06Ups10(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "b8.Payroll Unposting"


# Proxy of T06Prs10 for Self Services Payslip
class T06Ess05(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "Self Service Payslip"


# Attendance booking (imported from Time-attendance machine)
class T06Tam10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    payroll_period = models.ForeignKey(
        T06Prs10,
        models.PROTECT,
        db_column="IDPrlPeriod",
        null=True,
        related_name="machine_period_set",
    )
    attendance_date = models.DateTimeField(db_column="dtDate", null=True)
    attendance_day = models.CharField(db_column="sDay", max_length=50, blank=True)
    project_worked = models.BigIntegerField(db_column="IDAttPrj", blank=True, null=True)
    project = models.ForeignKey(
        T01Prj10, models.PROTECT, db_column="IDTbdPrj", null=True, blank=True
    )
    time_in = models.DateTimeField(db_column="dtTimeIn", null=True)
    entry_code = models.IntegerField(db_column="nEntryCode", null=True)
    time_out = models.DateTimeField(db_column="dtTimeOut", null=True)
    exit_code = models.IntegerField(db_column="nExitCode", null=True)
    weekend_flag = models.BooleanField(db_column="bWeekEnd", null=True)
    public_holiday_flag = models.BooleanField(db_column="bPubHoli", null=True)
    transaction_type = models.CharField(db_column="sTType", max_length=10, blank=True)
    attendance_note = models.TextField(db_column="sAttNotes", blank=True)
    lock_flag = models.BooleanField(
        db_column="bLocked", default=False
    )  # True when records inserted in T06TBM10

    class Meta:
        db_table = "T06TAM10"
        verbose_name = "b2.Access Control Machine Data"
        unique_together = (
            "employee_code",
            "attendance_date",
        )
        ordering = ["attendance_date"]

        def __str__(self):
            return f"{self.employee_code} - {self.attendance_date}"


# Time Booking Daily, data inserted from tables T06Tam10 OR manually entered
class T06Tbd10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    payroll_period = models.ForeignKey(
        T06Prs10,
        models.PROTECT,
        db_column="IDPrlPeriod",
        null=True,
        related_name="daily_period_set",
    )
    att_date = models.DateField(db_column="dTbdDate", null=True)
    att_day = models.CharField(db_column="sTbdDay", max_length=15, blank=True)
    project = models.ForeignKey(
        T01Prj10, models.PROTECT, db_column="IDTbdPrj", null=True, blank=True
    )
    normal_work_hrs = models.FloatField(
        db_column="fWrkhrs", default=0
    )  # normal_work_hrs = total working hours as per attendance
    normal_OT_hrs = models.FloatField(db_column="fOThrs", default=0)
    weekend_OT_hrs = models.FloatField(db_column="fWeOThrs", default=0)
    holiday_OT_hrs = models.FloatField(db_column="fPhOThrs", default=0)
    weekend_flag = models.BooleanField(db_column="bWeekEnd", default=False)
    public_holiday_flag = models.BooleanField(db_column="bPubHoli", default=False)
    paid_weekend = models.BooleanField(db_column="bPaidWeekEnd", default=True)
    paid_public_holiday = models.BooleanField(db_column="bPaidPubHoli", default=True)
    lock_flag = models.BooleanField(db_column="bLocked", default=False)

    class Meta:
        #    managed = False
        db_table = "T06TBD10"
        verbose_name = "b3.Daily Time Booking"
        unique_together = (
            "employee_code",
            "att_date",
        )
        ordering = (
            "employee_code",
            "att_date",
        )

    def __str__(self):
        return f"{self.employee_code} - {self.att_date}"

    def get_TAM_data(
        obj, ot_thresh=8
    ):  # ot_thresh = working_hours + addtional hours not eligible for OT .  meaning 8+1 = 9, after 9 hours work it is OT.
        """
        If any TAM data for the employee, then create the TBD data
        """
        logger.info(
            f"Reading TAM data and updating TBD table for all employees of {obj.division}-{obj.payroll_group} for month {obj.pay_month} and year {obj.pay_year} "
        )
        from django.db.models import F, Sum

        try:
            t06tbd10_objs_create = []
            payroll_period = obj

            for employee in T06Emp10.objects.all():
                t06tam10_queryset = T06Tam10.objects.filter(
                    employee_code=employee, payroll_period=payroll_period
                )

                if not t06tam10_queryset:
                    logger.info(
                        f"No Time machine attendance for the employee({employee.first_name}) in the TAM table for the given period"
                    )
                    continue

                # Group time attendance by date
                for t06tam10_obj in (
                    t06tam10_queryset.annotate(duration=F("time_out") - F("time_in"))
                    .values(
                        "attendance_date",
                        "attendance_day",
                        "weekend_flag",
                        "public_holiday_flag",
                    )
                    .annotate(total=Sum("duration"))
                ):

                    if t06tam10_obj.get("total"):
                        normal_work_hours = round(
                            (
                                ((t06tam10_obj.get("total", 0).total_seconds()) / 60)
                                / 60
                            ),
                            2,
                        )
                    else:
                        normal_work_hours = 0

                    public_holiday_flag = t06tam10_obj.get("public_holiday_flag", False)
                    weekend_flag = t06tam10_obj.get("weekend_flag", False)
                    holiday_OT_hrs, weekend_OT_hrs, normal_OT_hrs = 0, 0, 0

                    if public_holiday_flag:
                        holiday_OT_hrs = normal_work_hours
                        normal_work_hours = 0
                    elif weekend_flag:
                        weekend_OT_hrs = normal_work_hours
                        normal_work_hours = 0
                    else:
                        if normal_work_hours <= ot_thresh:
                            normal_OT_hrs = 0
                        else:
                            normal_OT_hrs = normal_work_hours - ot_thresh

                    t06tbd10_objs_create.append(
                        T06Tbd10(
                            employee_code=employee,
                            payroll_period=payroll_period,
                            att_date=t06tam10_obj.get("attendance_date"),
                            att_day=t06tam10_obj.get("attendance_day", None),
                            project=t06tam10_obj.get("project", None),
                            normal_work_hrs=normal_work_hours,
                            normal_OT_hrs=normal_OT_hrs,
                            weekend_OT_hrs=weekend_OT_hrs,
                            holiday_OT_hrs=holiday_OT_hrs,
                            weekend_flag=weekend_flag,
                            public_holiday_flag=public_holiday_flag,
                        )
                    )

            if t06tbd10_objs_create:
                T06Tbd10.objects.bulk_create(t06tbd10_objs_create)
                logger.info(f"Records created in TBD table")
                return

            logger.info(f"No Records created.")
            return
        except Exception as error:
            logger.error(str(error))
            return str(error)


# Time Booking Monthly, data inserted from tables T06Tam10 (OR) T06Tbd10
class T06Tbm10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    payroll_period = models.ForeignKey(
        T06Prs10,
        models.PROTECT,
        db_column="IDPrlPeriod",
        null=True,
        related_name="monthly_period_set",
    )
    project = models.ForeignKey(
        T01Prj10, models.PROTECT, db_column="IDTbmPrj", null=True, blank=True
    )
    normal_work_days = models.FloatField(db_column="fWrkdays", default=0)
    normal_OT_hrs = models.FloatField(db_column="fOThrs", default=0)
    holiday_OT_hrs = models.FloatField(db_column="fPhOThrs", default=0)
    weekend_OT_hrs = models.FloatField(db_column="fWeOThrs", default=0)
    total_weekend_days = models.FloatField(db_column="fTotWE", default=0)
    total_public_holidays = models.FloatField(db_column="fTotPH", default=0)
    total_unpaid_weekend_days = models.FloatField(db_column="uTotWE", default=0)
    total_unpaid_public_holidays = models.FloatField(db_column="uTotPH", default=0)
    lock_flag = models.BooleanField(
        db_column="bLocked", default=False
    )  # True when records saved in T06PRL10

    class Meta:
        db_table = "T06TBM10"
        verbose_name = "b4.Monthly Time Booking"
        unique_together = ("employee_code", "payroll_period", "project")
        ordering = (
            "employee_code",
            "payroll_period",
        )

    def __str__(self):
        return f"{self.employee_code} - {self.payroll_period} - {self.project}"

    def auto_entry(payroll_period: object):  # Later will check the logic
        #  Update of monthly bookking depend on working days
        t06tbm10_objs = T06Tbm10.objects.filter(payroll_period=payroll_period)
        for obj in t06tbm10_objs:
            # Get working days including weekends and public holidays
            loss_of_days = T06Lve10.lop_days(
                obj.employee_code, payroll_period.pay_month, payroll_period.pay_year
            )
            if loss_of_days > 0:
                working_days = loss_of_days
            else:
                working_days = get_no_of_days(
                    payroll_period.pay_month, payroll_period.pay_year
                )

            # update object for each employee
            obj.normal_work_days = working_days
            obj.save()

    def read_TBD_log(obj: object, ot_thresh=8):
        from django.db.models import Case, Count, Sum, When

        try:
            t06tbm10_objs_create, result, payroll_period = [], {}, obj
            # To store the result
            result["employees"] = []
            try:
                for t06tbd10_dict in (
                    T06Tbd10.objects.filter(payroll_period=payroll_period)
                    .values("employee_code", "project")
                    .annotate(
                        normal_OT_hrs=Sum("normal_OT_hrs"),
                        holiday_OT_hrs=Sum("holiday_OT_hrs"),
                        weekend_OT_hrs=Sum("weekend_OT_hrs"),
                        normal_work_days=Sum("normal_work_hrs"),
                        total_weekend_days=Count(Case(When(weekend_flag=True, then=1))),
                        total_public_holidays=Count(
                            Case(When(public_holiday_flag=True, then=1))
                        ),
                        total_unpaid_weekend=Count(
                            Case(When(paid_weekend=False, then=1))
                        ),
                        total_unpaid_public_holiday=Count(
                            Case(When(paid_public_holiday=False, then=1))
                        ),
                    )
                ):

                    normal_work_days = (
                        t06tbd10_dict["normal_work_days"]
                        / T06Emp10.objects.get(
                            id=t06tbd10_dict["employee_code"]
                        ).working_hr_per_day
                    )

                    data = {
                        "employee_code_id": t06tbd10_dict.get("employee_code", None),
                        "payroll_period": payroll_period,
                        "project": t06tbd10_dict.get("project", None),
                        "normal_work_days": normal_work_days,
                        "normal_OT_hrs": t06tbd10_dict.get("normal_OT_hrs", 0),
                        "holiday_OT_hrs": t06tbd10_dict.get("holiday_OT_hrs", 0),
                        "weekend_OT_hrs": t06tbd10_dict.get("weekend_OT_hrs", 0),
                        "total_weekend_days": t06tbd10_dict.get(
                            "total_weekend_days", 0
                        ),
                        "total_public_holidays": t06tbd10_dict.get(
                            "total_public_holidays", 0
                        ),
                        "total_unpaid_weekend_days": t06tbd10_dict.get(
                            "total_unpaid_weekend", 0
                        ),
                        "total_unpaid_public_holidays": t06tbd10_dict.get(
                            "total_unpaid_public_holiday", 0
                        ),
                    }
                    # Check the monthly data exists or not
                    tbm_obj = T06Tbm10.objects.filter(
                        employee_code_id=t06tbd10_dict.get("employee_code", None),
                        payroll_period=payroll_period,
                    )

                    if tbm_obj.exists():
                        tbm_obj.update(**data)
                    else:
                        t06tbm10_objs_create.append(T06Tbm10(**data))

            except Exception as error:
                logger.error(str(error))
                result["employees"].append({"error": str(error)})

            if t06tbm10_objs_create:
                T06Tbm10.objects.bulk_create(t06tbm10_objs_create)
                return result

            logger.info(f"No Records created.")
            return result
        except Exception as error:
            logger.error(str(error))
            result["error"] = str(error)
            return result


# Proxy of T06Tbm10 for Self Services Monthly Time Booking
class T06Ess06(T06Tbm10):
    class Meta:
        proxy = True
        verbose_name = "Self Service Monthly Timesheet"


"""
    # automatic attendance booking for certain category of employees
    def auto_attendance(emp_cat, payroll_period):

        # Find number of working days form T06Lve10 class def functions
        # working days = find_days_in_month() - availed_days()
        # no 'OT' for this category of employees
        # Insert attendance records in T06TBM10 table for the payroll period

        return
"""

# Leave4 data Entry part of attendance data capture
class T06Lve10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    leave_code = models.ForeignKey(
        "T06Lvr10", models.PROTECT, db_column="IDLVR10", null=True
    )
    LVESTATUS_CHOICE = (("1", "Pending"), ("2", "Approved"), ("3", "Rejected"))
    leave_status = models.CharField(
        db_column="sLveStatus", max_length=1, choices=LVESTATUS_CHOICE, default="1"
    )
    REQUEST_CHOICE = (("1", "Utilize Leave"), ("2", "Encash Leave"))
    request_type = models.CharField(
        db_column="sReqType", max_length=1, choices=REQUEST_CHOICE, default="1"
    )
    request_date_from = models.DateTimeField(db_column="dtReqFrom", null=True)
    request_date_to = models.DateTimeField(db_column="dtReqTo", null=True)
    request_note = models.TextField(db_column="sReqNote", blank=True)
    user_approved = models.ForeignKey(
        T06Emp10,
        models.PROTECT,
        related_name="lveapprover",
        db_column="IDLveAppr",
        blank=True,
        null=True,
    )
    dt_of_approval = models.DateTimeField(
        db_column="dtApprvdDataEntry", blank=True, null=True
    )
    approver_note = models.TextField(db_column="sAprvNote", blank=True)
    approved_from_date = models.DateTimeField(
        db_column="dtApprFrom", blank=True, null=True
    )
    approved_to_date = models.DateTimeField(db_column="dtApprTo", blank=True, null=True)
    actual_date_from = models.DateTimeField(
        db_column="dtActFrom", blank=True, null=True
    )
    actual_date_to = models.DateTimeField(db_column="dtActTo", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T06LVE10"
        verbose_name = "c1.Leave Application"
        ordering = ("id",)

    def save(self, **kwargs):
        self.clean()
        return super(T06Lve10, self).save(**kwargs)

    def clean(self):
        super(T06Lve10, self).clean()

        if (
            self.approved_to_date
            and self.approved_from_date
            and self.approved_to_date < self.approved_from_date
        ):
            raise ValidationError(
                {
                    "approved_to_date": "approved to date to must be greater than or equal to approved from date"
                }
            )

        if (
            self.actual_date_to
            and self.actual_date_from
            and self.actual_date_to < self.actual_date_from
        ):
            raise ValidationError(
                {
                    "actual_date_to": "actual date to must be greater than or equal to actual date from"
                }
            )

        if (
            self.approved_to_date
            and self.actual_date_to
            and self.approved_to_date > self.actual_date_to
        ):
            raise ValidationError(
                {
                    "approved_to_date": "approved to date to must be less than or equal to actual to date"
                }
            )

        if (
            self.approved_from_date
            and self.actual_date_from
            and self.approved_from_date < self.actual_date_from
        ):
            raise ValidationError(
                {
                    "approved_to_date": "approved from date to must be grater or equal to actual from date"
                }
            )

        if self.request_date_to and self.request_date_from:
            if self.request_date_to < self.request_date_from:
                raise ValidationError(
                    {
                        "request_date_to": "Request date to must be greater than or equal to request date from"
                    }
                )

            # if payroll run setup att_flag = True, no insert edit, delete for the month
            if (
                T06Prs10.objects.filter(
                    models.Q(
                        pay_year=self.request_date_from.year,
                        pay_month=self.request_date_from.month,
                    )
                    | models.Q(
                        pay_year=self.request_date_to.year,
                        pay_month=self.request_date_to.month,
                    )
                )
                .filter(att_lock_flag=True)
                .exists()
            ):

                raise ValidationError(
                    "The payroll setup has been locked for this month."
                )

    def __str__(self) -> str:
        return f"{self.employee_code},{self.leave_code}"

    def find_days(date2, date1):
        return (date2 - date1).days

    def find_days_in_month(month, year, from_date, to_date):
        if from_date > to_date:
            raise Exception("From date cannot be less than to date! Please check.")
        days = 0
        start_date = timezone.make_aware(
            timezone.datetime(year, month, 1), timezone=None
        )
        last_day = monthrange(year, month)[1]
        end_date = timezone.make_aware(
            timezone.datetime(year, month, last_day), timezone=None
        )

        if from_date.month == month and to_date.month == month:
            days = T06Lve10.find_days(to_date, from_date) + 1

        elif from_date.month != month and to_date.month != month:
            if from_date > end_date:
                days = 0
            elif to_date < start_date:
                days = 0
            elif from_date < start_date and to_date > end_date:
                days = last_day

        elif from_date.month == month and to_date.month != month:
            days = last_day - from_date.day + 1

        elif from_date.month != month and to_date.month == month:
            first_day = 1
            days = to_date.day - first_day + 1
        return days

    def lop_days(employee, month, year):
        # Get loss of pay days or get working days
        #  based on approved days and actual days in the payroll_month
        lop = 0
        leaves = T06Lve10.objects.filter(employee_code=employee)
        for leave in leaves:
            if (
                leave.approved_from_date
                and leave.approved_to_date
                and leave.actual_date_from
                and leave.actual_date_to
            ):
                approved_days = T06Lve10.find_days_in_month(
                    month, year, leave.approved_from_date, leave.approved_to_date
                )
                actual_days = T06Lve10.find_days_in_month(
                    month, year, leave.actual_date_from, leave.actual_date_to
                )
                act_app_diff = actual_days - approved_days
                if act_app_diff > 0:
                    lop += act_app_diff
        return lop

    def pay_days(lvecode, employee, month, year):
        leaves = T06Lve10.objects.filter(employee_code=employee, leave_code=lvecode)
        pay_days = 0
        for leave in leaves:
            from_month = leave.approved_from_date
            to_month = leave.approved_to_date
            approved_days = T06Lve10.find_days_in_month(
                month, year, from_month, to_month
            )
            pay_days += approved_days
        return pay_days

    def availed_days(lvecode, employee, month, year):
        leaves = T06Lve10.objects.filter(employee_code=employee).filter(
            leave_code=lvecode
        )
        leaves_availed = 0
        for leave in leaves:
            from_month = leave.actual_date_from
            to_month = leave.actual_date_to
            leaves_availed += T06Lve10.find_days_in_month(
                month, year, from_month, to_month
            )
        try:
            t06emp12_obj = T06Emp12.objects.get(employee_code=employee)
            t06emp12_obj.leave_availed = leaves_availed
            t06emp12_obj.save(update_fields=["leave_availed"])
        except T06Emp12.DoesNotExist:
            logger.error("T06Emp12 object doesn't exist")
        return leaves_availed


# Proxy of T06Lve10 for Self Services Leaves
class T06Ess01(T06Lve10):
    class Meta:
        proxy = True
        verbose_name = "Self Service Leave app"


# for next version use to validate weekend / public holidays
class T06Phd10(models.Model):
    public_holiday = models.DateField(db_column="dPubHoli", null=True)
    public_holiday_desc = models.CharField(
        db_column="sPubHoliDesc", max_length=50, blank=True
    )

    class Meta:
        #    managed = False
        db_table = "T06PHD10"
        verbose_name = "Public Holiday"

    def __str__(self) -> str:
        return f"{self.public_holiday}"

    def no_of_phdays(period):
        no_of_phd = 5  # filter.month()
        return no_of_phd

    def no_of_weekends(period):
        no_of_wends = 8  # logic to find Weekends
        return no_of_wends

    def is_it_phday(dt):
        if dt in T06Phd10.public_holiday:
            return True
        else:
            return False

    def is_it_weekend(dt):
        if dt.weekday() in T01Dsg10.weekend_days:
            return True
        else:
            return False

    def validate_weekend_flag():
        pass

    def validate_pubholiday_flag():
        pass
