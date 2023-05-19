import datetime
import logging
import sys
from calendar import monthrange

from django.db import models
from django.db.models import F, Sum
from django.utils import timezone

from ebos2201.models.m01_fin_mas import T01Prj10
from ebos2201.utils import get_no_of_days

from .m06_att_trn import T06Lve10, T06Prs10, T06Tbm10
from .m06_emp_mas import T06Emp10, T06Emp12, T06Emp13, T06Emp14, T06Emp15, T06Emp16
from .m06_hr_mas import T06Cfg10, T06Lvr10

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
  # Call functions in the following order only.
	T06Prl10.get_monthly_att(payroll_period)
	T06Prl12.insert_t06prl12(payroll_period)
	T06Prl13.insert_t06prl13(payroll_period)
	T06Prl14.insert_t06prl14(payroll_period) # or T06Prl14.update_t06prl14(payroll_period)
	T06Prl15.insert_t06prl15(payroll_period) # or T06Prl15.update_t06prl15(payroll_period)
	T06Prl16.insert_t06prl16(payroll_period) # or T06Prl16.update_t06prl16(payroll_period)
	T06Prl10.update_monthly_att(payroll_period)
    T06Prl12.update_t06prl12(payroll_period)
	T06Prl12.update_t06emp12(payroll_period)
	T06Prl11.insert_t06prl11(payroll_period) # or T06Prl11.update_t06prl11(payroll_period)
"""

# Payroll processing header table


class T06Prl10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    payroll_period = models.ForeignKey(
        T06Prs10,
        models.PROTECT,
        db_column="IDPrlPeriod",
        null=True,
        related_name="payroll_set",
    )
    tot_days_worked = models.IntegerField(
        db_column="nPayableDays", null=True
    )  # include weekend and public holidays
    tot_ot_hours = models.FloatField(db_column="fOTHrs", blank=True, null=True)
    tot_ML_days = models.FloatField(db_column="fTMLDays", null=True)
    tot_EL_days = models.FloatField(db_column="fTELDays", null=True)
    tot_LOP_days = models.FloatField(db_column="fTLOPDays", null=True)
    tot_ABS_days = models.FloatField(
        db_column="fTABSDays", null=True
    )  # Manual Entry for now
    tot_SubCont_days = models.FloatField(
        db_column="fTSCDays", null=True
    )  # Manual Entry for now
    gratuity_provision = models.FloatField(db_column="fGratProv", null=True)
    ticket_provision = models.FloatField(db_column="fTktProv", null=True)
    leavepay_provision = models.FloatField(db_column="fLveProv", null=True)
    basic_pay = models.FloatField(db_column="fBasic", null=True)
    ot_pay = models.FloatField(db_column="fOTpay", blank=True, null=True)
    ml_pay = models.FloatField(db_column="fMLpay", blank=True, null=True)
    el_pay = models.FloatField(db_column="fELpay", blank=True, null=True)
    other_pay = models.FloatField(db_column="fOtherpay", blank=True, null=True)
    tkt_pay = models.FloatField(db_column="fTKTpay", blank=True, null=True)
    wps_housing_amt = models.FloatField(db_column="fWpHouseamt", blank=True, null=True)
    wps_transport_amt = models.FloatField(
        db_column="fWpTransamt", blank=True, null=True
    )
    fixed_alw = models.FloatField(db_column="fFixAlw", null=True)
    variable_alw = models.FloatField(db_column="fvarAlw", null=True)
    deductions = models.FloatField(db_column="fDeductions", null=True)
    loan_emi = models.FloatField(db_column="fLoanEmi", null=True)
    round_off = models.FloatField(db_column="fRnd", null=True)
    gl_code = models.IntegerField(db_column="nPrlGLCode", blank=True, null=True)
    gl_voucher = models.BigIntegerField(
        db_column="IDGlVou", blank=True, null=True
    )  # IF > 0, it is a posted entry

    class Meta:
        #    managed = False
        db_table = "T06PRL10"
        verbose_name = "b6.Payroll Summary"
        verbose_name_plural = "b6.Payroll Summary"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.employee_code},{self.payroll_period}"

    # insert attendance record for the payroll period in T06PRL10 from the class T06TBM10
    # by aggregating data by month by employee
    def get_monthly_att(payroll_period):
        t06Prl10_objs_create = []

        for t06TBM10_obj in (
            T06Tbm10.objects.filter(
                payroll_period=payroll_period, employee_code__employee_status=1
            )
            .values(
                "employee_code",
                "total_weekend_days",
                "total_public_holidays",
                "total_unpaid_weekend_days",
                "total_unpaid_public_holidays",
            )
            .annotate(
                total_normal_OT_hrs=Sum("normal_OT_hrs"),
                total_holiday_OT_hrs=Sum("holiday_OT_hrs"),
                total_weekend_OT_hrs=Sum("weekend_OT_hrs"),
                total_normal_work_days=Sum("normal_work_days"),
            )
            .annotate(
                tot_ot_hours=F("total_normal_OT_hrs")
                + F("total_holiday_OT_hrs")
                + F("total_weekend_OT_hrs")
            )
        ):

            try:
                t06Prl10_objs_create.append(
                    T06Prl10(
                        employee_code_id=t06TBM10_obj.get("employee_code", None),
                        payroll_period=payroll_period,
                        tot_days_worked=t06TBM10_obj.get("total_normal_work_days", 0)
                        + t06TBM10_obj["total_weekend_days"]
                        + t06TBM10_obj["total_public_holidays"]
                        - t06TBM10_obj["total_unpaid_weekend_days"]
                        - t06TBM10_obj["total_unpaid_public_holidays"],
                        tot_ot_hours=t06TBM10_obj.get("tot_ot_hours", 0),
                    )
                )
            except Exception as error:
                logger.error(f"{error} in get_monthly_att() for creating objects")
                continue

        try:
            T06Prl10.objects.bulk_create(t06Prl10_objs_create)
        except Exception as error:
            logger.error(f"Error:{error} in get_monthly_att() bulk_create")
            return {"status": "Failed", "error": str(error)}

    def update_monthly_att(payroll_period):
        t06Prl10_objs = T06Prl10.objects.filter(payroll_period=payroll_period)
        for t06Prl10_obj in t06Prl10_objs:
            try:
                t06Prl10_obj.basic_pay = t06Prl10_obj.basic()
                t06Prl10_obj.ot_pay = t06Prl10_obj.otpay()
                t06Prl10_obj.ml_pay = t06Prl10_obj.ml_amount()
                t06Prl10_obj.other_pay = t06Prl10_obj.Other_lvepay_amt()
                t06Prl10_obj.el_pay = t06Prl10_obj.el_amount()
                t06Prl10_obj.tkt_pay = t06Prl10_obj.ticket_amt()
                (
                    t06Prl10_obj.fixed_alw,
                    t06Prl10_obj.variable_alw,
                ) = t06Prl10_obj.get_alw()
                t06Prl10_obj.deductions = t06Prl10_obj.deduction_amt()
                t06Prl10_obj.round_off = t06Prl10_obj.roundoff()
                t06Prl10_obj.gratuity_provision = t06Prl10_obj.get_gratuity_provision()
                t06Prl10_obj.leavepay_provision = t06Prl10_obj.get_leavepay_provision()
                t06Prl10_obj.ticket_provision = t06Prl10_obj.get_ticket_provision()

                t06Prl10_obj.loan_emi = T06Prl15.prl_loan_emi(t06Prl10_obj.id)
                t06Prl10_obj.tot_LOP_days = T06Lve10.lop_days(
                    t06Prl10_obj.employee_code,
                    payroll_period.pay_month,
                    payroll_period.pay_year,
                )
                try:
                    leave_code = T06Lvr10.objects.get(leave_code="ML")
                    t06Prl10_obj.tot_ML_days = t06Prl10_obj.get_leave_days(
                        leave_code=leave_code
                    )
                except:
                    pass

                try:
                    leave_code = T06Lvr10.objects.get(leave_code="EL")
                    t06Prl10_obj.tot_EL_days = t06Prl10_obj.get_leave_days(
                        leave_code=leave_code
                    )
                except:
                    pass

                t06Prl10_obj.tkt_pay = t06Prl10_obj.ticket_amt()
            except Exception as error:
                logger.error(f"Error in update_monthly_att: {error} ")
                raise error

        try:
            T06Prl10.objects.bulk_update(
                t06Prl10_objs,
                [
                    "basic_pay",
                    "ot_pay",
                    "ml_pay",
                    "other_pay",
                    "el_pay",
                    "tkt_pay",
                    "fixed_alw",
                    "variable_alw",
                    "deductions",
                    "round_off",
                    "gratuity_provision",
                    "leavepay_provision",
                    "ticket_provision",
                    "loan_emi",
                    "tot_LOP_days",
                    "tot_ML_days",
                    "tot_EL_days",
                    "tkt_pay",
                ],
            )
        except Exception as error:
            logger.error(f"Error during T06Prl10 objects updation: {error} ")

    def paydays(year, month):
        """Returns Number of days in a month for payroll purpose"""

        t06Cfg10_obj = T06Cfg10.objects.all().first()

        if t06Cfg10_obj.pay_perday_div == "M":
            pr_mn_days = monthrange(year, month)[1]
        elif t06Cfg10_obj.pay_perday_div == "Y":
            pr_mn_days = 365 / 12
        else:
            pr_mn_days = 30

        return pr_mn_days

    @property
    def reco_att(self):  # Reconcile attendance data
        return (
            self.tot_days_worked
            + self.tot_ML_days
            + self.tot_EL_days
            + self.tot_LOP_days
            + self.tot_ABS_days
            + self.tot_SubCont_days
        ) == T06Prl10.paydays(
            self.payroll_period.pay_year, self.payroll_period.pay_month
        )

    def pay_per_day(self):
        pay_perday = self.employee_code.basic_pay + self.alw_pay() / T06Prl10.paydays(
            self.payroll_period.pay_year, self.payroll_period.pay_month
        )
        return pay_perday

    def basic(self):
        basic_pay = self.tot_days_worked * (
            self.employee_code.basic_pay
            / get_no_of_days(
                self.payroll_period.pay_month, self.payroll_period.pay_year
            )
        )
        return round(basic_pay, 2)

    def otpay(self):
        ot_rate_per_hr = (
            self.employee_code.basic_pay
            / T06Prl10.paydays(
                self.payroll_period.pay_year, self.payroll_period.pay_month
            )
            / self.employee_code.working_hr_per_day
        )

        if self.employee_code.designation:
            ot_rate_per_hr = ot_rate_per_hr * self.employee_code.designation.ot_multiplier

        return self.tot_ot_hours * ot_rate_per_hr

    def ml_amount(self):
        try:
            leave_code = T06Lvr10.objects.get(leave_code="ML")
            pay_days = T06Lve10.pay_days(
                lvecode=leave_code,
                employee=self.employee_code,
                month=self.payroll_period.pay_month,
                year=self.payroll_period.pay_year,
            )
            t06Emp12_dict = T06Prl12.get_leaves_availed(
                self.employee_code, leave_code=leave_code
            )
            if not t06Emp12_dict:
                return 0
            leave_availed = t06Emp12_dict[0].get("leave_availed__sum")

            pay_ratio = T06Prl12.get_pay_ratio(leave_availed, pay_days)

            return round(pay_days * self.pay_per_day() * pay_ratio, 2)
        except:
            return 0

    def el_amount(
        self,
    ):  # multiple records may be in T06Prl12, function input param (empcode, "EL", month, year)
        try:
            leave_code = T06Lvr10.objects.get(leave_code="EL")
            pay_days = T06Lve10.pay_days(
                lvecode=leave_code,
                employee=self.employee_code,
                month=self.payroll_period.pay_month,
                year=self.payroll_period.pay_year,
            )
            return pay_days * self.pay_per_day()
        except Exception as error:
            logger.error(str(error))
            return 0

    def get_leave_days(self, leave_code):
        try:
            t06Prl12_objs = T06Prl12.objects.filter(
                payroll_id=self, leave_code=leave_code
            )
            if not t06Prl12_objs:
                return 0
            return t06Prl12_objs[0].leave_days
        except Exception as error:
            logger.error(str(error))
            return 0

    # multiple records may be in T06Prl12
    def Other_lvepay_amt(self):
        # Execute functions in T06Prl12, input parameters (empcode, lveCode-excluding-ML-EL, month, year)
        leave_codes = T06Lvr10.objects.exclude(leave_code__in=["ML", "EL"])
        pay_days = 0
        for leave_code in leave_codes:
            pay_days += T06Lve10.pay_days(
                lvecode=leave_code,
                employee=self.employee_code,
                month=self.payroll_period.pay_month,
                year=self.payroll_period.pay_year,
            )
        return pay_days * self.pay_per_day()

    def get_alw(self):
        fixed, variable = 0, 0

        try:
            for t06Prl13_obj in T06Prl13.objects.filter(payroll_id=self.id):
                a, b = t06Prl13_obj.alw_amt()
                fixed += a
                variable += b
        except T06Prl13.DoesNotExist:
            logger.error("T06Prl13 object doesn't exist.")

        return fixed, variable

    def alw_pay(self):
        fixed_alw, variable_alw = self.get_alw()
        tot_alw = fixed_alw + variable_alw
        return tot_alw

    def deduction_amt(self):  # multiple records may be in T06Prl16
        # Execute functions in T06Prl16 monthly deductions, input parameters (empcode, month, year)
        # Execute functions in T06Prl15 Loan deductions, input parameters (empcode, month, year)
        return T06Prl16.prl_deductions(self) + T06Prl15.prl_loan_ded(self)

    def ticket_amt(self):
        # Execute functions in T06Prl14 ticket claims, input parameters (empcode, month, year)
        return T06Prl14.prl_ticket_amt(self)

    def get_gratuity_provision(self):
        return round(self.basic_pay * (2.5 / 30), 2)

    def get_ticket_provision(self):
        try:
            t06Emp14_obj = T06Emp14.objects.get(employee_code=self.employee_code)
            return round(t06Emp14_obj.ticket_amount / 2)
        except Exception as error:
            logger.error(f"{error}")
            return 0

    def get_leavepay_provision(self):
        return round(self.basic_pay * (2.5 / 30), 2)

    @property
    def grosspay(self):  # basic + OTpay + FixedAlw + VariableAlw
        gp = self.basic_pay + self.ot_pay + self.fixed_alw + self.variable_alw
        return gp

    @property
    def netpay(self):
        netpay = self.grosspay - self.deduction_amt()  # - deductions
        return netpay

    def roundoff(self):
        original_amt = self.netpay
        round_amt = round(original_amt)
        return round_amt - original_amt

    # def update_t06emp10(payroll_period:object):
    # 	payroll_obj = T06Prl10.objects.filter(payroll_period=payroll_period).first()
    # 	if payroll_obj:
    # 		T06Emp10_obj = T06Emp10.objects.filter(employee_code = payroll_obj.employee_code).first()
    # 		T06Prs10_obj = T06Prs10.objects.get(id = payroll_obj.payroll_period.id)
    # 		pay_year = T06Prs10_obj.pay_year
    # 		pay_month = T06Prs10_obj.pay_month
    # 		date = datetime.date(2021,5,16)
    # 		last_day_of_month = date.replace(day = calendar.monthrange(pay_year, pay_month)[1])

    # 		try:
    # 			# Update last_day_of_month field in T06Emp10
    # 			update_t06emp10 = T06Emp10_obj.update(date_last_payroll = last_day_of_month)
    # 		except Exception as error:
    # 			logger.error(f"Error:{error}")
    # 			return {"status": "Failed", "error": str(error)}


class T06Prl11(models.Model):
    payroll_id = models.ForeignKey(
        T06Prl10, on_delete=models.CASCADE, db_column="IDROLL10", null=True
    )
    project = models.ForeignKey(
        T01Prj10, models.PROTECT, db_column="IDPrlPrj", blank=True, null=True
    )
    prj_work_days = models.IntegerField(db_column="nDays", null=True)
    prj_ot_hours = models.FloatField(db_column="fOTHrs", blank=True, null=True)
    prj_allowance = models.FloatField(db_column="fvarAlw", blank=True, null=True)
    prj_labour_cost = models.FloatField(db_column="fLabourCost", null=True)

    class Meta:
        #    managed = False
        db_table = "T06PRL11"
        verbose_name = "Labour Cost by Project"
        ordering = ("id",)

    def __str__(self):
        return f"{self.project}"

    def insert_t06prl11(payroll_period):
        t06Prl11_create = []

        for t06TBM10_obj in (
            T06Tbm10.objects.filter(payroll_period=payroll_period)
            .values("employee_code", "project")
            .annotate(
                total_normal_OT_hrs=Sum("normal_OT_hrs"),
                total_holiday_OT_hrs=Sum("holiday_OT_hrs"),
                total_weekend_OT_hrs=Sum("weekend_OT_hrs"),
                total_normal_work_days=Sum("normal_work_days"),
            )
            .annotate(
                prj_ot_hours=F("total_normal_OT_hrs")
                + F("total_holiday_OT_hrs")
                + F("total_weekend_OT_hrs")
            )
        ):
            try:
                # default to project id=1 if project is None
                project = T01Prj10.objects.get(id=t06TBM10_obj.get("project", 1))
                employee_code = t06TBM10_obj.get("employee_code")
                prj_ot_hours = t06TBM10_obj.get("prj_ot_hours", 0)
                prj_work_days = t06TBM10_obj.get("total_normal_work_days")
                payroll_id = T06Prl10.objects.get(
                    employee_code=employee_code, payroll_period=payroll_period
                )

                try:
                    prj_allowance = (
                        (payroll_id.fixed_alw + payroll_id.variable_alw)
                        / payroll_id.tot_days_worked
                    ) * prj_work_days
                except ZeroDivisionError:
                    prj_allowance = 0

                prj_labour_cost = T06Prl11.prj_hr_cost(
                    payroll_id, prj_work_days, prj_ot_hours, prj_allowance
                )
                t06Prl11_create.append(
                    T06Prl11(
                        payroll_id=payroll_id,
                        project=project,
                        prj_work_days=prj_work_days,
                        prj_ot_hours=prj_ot_hours,
                        prj_allowance=prj_allowance,
                        prj_labour_cost=prj_labour_cost,
                    )
                )
            except Exception as error:
                logger.error(f"Error in appending T06Prl11 object:{error}")
                continue

        if t06Prl11_create:
            try:
                T06Prl11.objects.bulk_create(t06Prl11_create)
                return {"status": "Successful", "error": None}
            except Exception as error:
                logger.error(f"Error in creating T06Prl11 bulk objects:{error}")
                return {"status": "Failed", "error": str(error)}

    def update_t06prl11(payroll_period):
        t06Prl11_create = []
        t06Prl11_update = []

        for t06TBM10_obj in (
            T06Tbm10.objects.filter(payroll_period=payroll_period)
            .values("employee_code", "project")
            .annotate(
                total_normal_OT_hrs=Sum("normal_OT_hrs"),
                total_holiday_OT_hrs=Sum("holiday_OT_hrs"),
                total_weekend_OT_hrs=Sum("weekend_OT_hrs"),
                total_normal_work_days=Sum("normal_work_days"),
            )
            .annotate(
                prj_ot_hours=F("total_normal_OT_hrs")
                + F("total_holiday_OT_hrs")
                + F("total_weekend_OT_hrs")
            )
        ):
            try:
                # default to project id=1 if project is None
                project = T01Prj10.objects.get(id=t06TBM10_obj.get("project", 1))

                employee_code = t06TBM10_obj.get("employee_code")
                prj_ot_hours = t06TBM10_obj.get("prj_ot_hours", 0)
                prj_work_days = t06TBM10_obj.get("total_normal_work_days")
                payroll_id = T06Prl10.objects.get(
                    employee_code=employee_code, payroll_period=payroll_period
                )
                try:
                    prj_allowance = (
                        (payroll_id.fixed_alw + payroll_id.variable_alw)
                        / payroll_id.tot_days_worked
                    ) * prj_work_days
                except ZeroDivisionError:
                    prj_allowance = 0

                prj_labour_cost = T06Prl11.prj_hr_cost(
                    payroll_id, prj_work_days, prj_ot_hours, prj_allowance
                )

                queryset = T06Prl11.objects.filter(
                    payroll_id=payroll_id, project=project
                )
                if queryset.exists():
                    for obj in queryset:
                        obj.prj_work_days = prj_work_days
                        obj.prj_ot_hours = prj_ot_hours
                        obj.prj_allowance = prj_allowance
                        obj.prj_labour_cost = prj_labour_cost
                    t06Prl11_update.extend(queryset)
                else:
                    t06Prl11_create.append(
                        T06Prl11(
                            payroll_id=payroll_id,
                            project=project,
                            prj_work_days=prj_work_days,
                            prj_ot_hours=prj_ot_hours,
                            prj_allowance=prj_allowance,
                            prj_labour_cost=prj_labour_cost,
                        )
                    )
            except Exception as error:
                logger.error(f"Error in appending T06Prl11 object:{error}")
                continue

        if t06Prl11_create:
            try:
                T06Prl11.objects.bulk_create(t06Prl11_create)
                return {"status": "Successful", "error": None}
            except Exception as error:
                logger.error(f"Error in creating T06Prl11 bulk objects:{error}")
                return {"status": "Failed", "error": str(error)}

        if t06Prl11_update:
            try:
                T06Prl11.objects.bulk_update(
                    t06Prl11_update,
                    [
                        "prj_work_days",
                        "prj_ot_hours",
                        "prj_allowance",
                        "prj_labour_cost",
                    ],
                )
                return {"status": "Successful", "error": None}
            except Exception as error:
                logger.error(f"Error during T06Prl11 objects updation: {error} ")
                return {"status": "Failed", "error": str(error)}

    def prj_hr_cost(payroll_id, prj_work_days, prj_ot_hours, prj_allowance):
        try:
            labour = (
                (payroll_id.basic_pay + payroll_id.fixed_alw)
                / payroll_id.tot_days_worked
                * prj_work_days
            ) + (
                (payroll_id.ot_pay / payroll_id.tot_ot_hours * prj_ot_hours)
                + prj_allowance
            )
            return labour
        except ZeroDivisionError:
            return 0


class T06Prl12(models.Model):
    payroll_id = models.ForeignKey(
        T06Prl10, on_delete=models.CASCADE, db_column="IDROLL10", null=True
    )
    leave_code = models.ForeignKey(T06Lvr10, models.PROTECT, null=True)
    leave_days = models.FloatField(db_column="fDays", null=True)
    leave_pay_days = models.FloatField(db_column="fDaysWPay", null=True)
    leave_pay_amount = models.FloatField(db_column="fLvePayAmt", null=True)
    encash_days = models.IntegerField(db_column="nEncashDays", null=True)
    encash_amount = models.FloatField(db_column="nEncashAmt", null=True)
    accrued_days = models.FloatField(db_column="nDaysAccrued", null=True)

    class Meta:
        #    managed = False
        db_table = "T06PRL12"
        verbose_name = "Payroll Leave Amount"
        ordering = ("id",)

    def __str__(self):
        return f"{self.leave_code}"

    def insert_t06prl12(payroll_period: object):
        t06Prl12_create = []
        leave_codes_dict = {leave.leave_code: leave for leave in T06Lvr10.objects.all()}

        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            try:
                leave_codes = T06Lve10.objects.filter(
                    employee_code=payroll_id.employee_code
                ).values_list("leave_code__leave_code")
                if not leave_codes:
                    continue
                for leave_code in leave_codes[0]:
                    try:
                        leave_code = leave_codes_dict[leave_code]
                        leave_days = T06Lve10.availed_days(
                            leave_code,
                            payroll_id.employee_code,
                            payroll_period.pay_month,
                            payroll_period.pay_year,
                        )
                        leave_pay_days = T06Lve10.pay_days(
                            leave_code,
                            payroll_id.employee_code,
                            payroll_period.pay_month,
                            payroll_period.pay_year,
                        )
                        accrued_days = 2.5

                        t06Prl12_create.append(
                            T06Prl12(
                                payroll_id=payroll_id,
                                leave_code=leave_code,
                                leave_days=leave_days,
                                leave_pay_days=leave_pay_days,
                                accrued_days=accrued_days,
                            )
                        )
                    except Exception as error:
                        logger.error(f"Error in creating T06Prl12 object:{error}")
                        continue
            except Exception as error:
                logger.error(f"Error in insert_t06prl12:{error}")
                continue

        if t06Prl12_create:
            try:
                T06Prl12.objects.bulk_create(t06Prl12_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl12 bulk objects:{error}")

    def update_t06prl12(payroll_period):
        t06Prl12_create = []
        t06Prl12_update = []
        leave_codes_dict = {}
        for leave in T06Lvr10.objects.all():
            leave_codes_dict[leave.leave_code] = leave

        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            try:
                leave_codes = T06Lve10.objects.filter(
                    employee_code=payroll_id.employee_code
                ).values_list("leave_code__leave_code")
                if not leave_codes:
                    continue
                for leave_code in leave_codes[0]:
                    try:
                        leave_code = leave_codes_dict[leave_code]
                        leave_days = T06Lve10.availed_days(
                            leave_code,
                            payroll_id.employee_code,
                            payroll_period.pay_month,
                            payroll_period.pay_year,
                        )
                        leave_pay_days = T06Lve10.pay_days(
                            leave_code,
                            payroll_id.employee_code,
                            payroll_period.pay_month,
                            payroll_period.pay_year,
                        )
                        accrued_days = 2.5
                        leave_pay_amount = T06Prl12.leave_pay(
                            leave_code=leave_code,
                            payroll_id=payroll_id,
                            leave_pay_days=leave_pay_days,
                        )
                        encash_days, encash_amount = T06Prl12.lve_encashment(payroll_id)

                        queryset = T06Prl12.objects.filter(
                            payroll_id=payroll_id, leave_code=leave_code
                        )
                        if queryset.exists():
                            for obj in queryset:
                                obj.leave_days = leave_days
                                obj.leave_pay_days = leave_pay_days
                                obj.leave_pay_amount = leave_pay_amount
                                obj.encash_days = encash_days
                                obj.encash_amount = encash_amount
                                obj.accrued_days = accrued_days

                            t06Prl12_update.extend(queryset)
                        else:
                            t06Prl12_create.append(
                                T06Prl12(
                                    payroll_id=payroll_id,
                                    leave_code=leave_code,
                                    leave_days=leave_days,
                                    leave_pay_days=leave_pay_days,
                                    leave_pay_amount=leave_pay_amount,
                                    encash_days=encash_days,
                                    encash_amount=encash_amount,
                                    accrued_days=accrued_days,
                                )
                            )
                    except Exception as error:
                        logger.error(f"Error in creating t06prl12 object:{error}")
                        continue
            except Exception as error:
                logger.error(f"Error in update_t06prl12:{error}")
                continue

        if t06Prl12_create:
            try:
                T06Prl12.objects.bulk_create(t06Prl12_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl12 bulk objects:{error}")

        if t06Prl12_update:
            try:
                T06Prl12.objects.bulk_update(
                    t06Prl12_update,
                    [
                        "leave_days",
                        "leave_pay_days",
                        "leave_pay_amount",
                        "encash_days",
                        "encash_amount",
                        "accrued_days",
                    ],
                )
            except Exception as error:
                logger.error(f"Error during T06Prl12 objects updation: {error} ")

    def get_pay_ratio(leave_availed, leave_pay_days):
        if leave_availed + leave_pay_days > 45:
            pay_ratio = 0
        elif leave_availed + leave_pay_days > 30:
            pay_ratio = 0.5
        elif (
            leave_availed + leave_pay_days > 0 and leave_availed + leave_pay_days <= 30
        ):
            pay_ratio = 1
        else:
            pay_ratio = 0

        return pay_ratio

    def leave_pay(leave_code, payroll_id, leave_pay_days):
        # based on actual leave utilized from T06Lve10
        lvepay = 0
        if leave_code.leave_code == "ML":
            from django.db.models import Sum

            t06Emp12_dict = T06Prl12.get_leaves_availed(
                payroll_id.employee_code, leave_code=leave_code
            )
            if not t06Emp12_dict:
                return 0
            leave_availed = t06Emp12_dict[0].get("leave_availed__sum")
            pay_ratio = T06Prl12.get_pay_ratio(leave_availed, leave_pay_days)
            lvepay += leave_pay_days * payroll_id.pay_per_day() * pay_ratio

        else:
            lvepay = leave_pay_days * payroll_id.pay_per_day()
        return lvepay

    def lve_encashment(payroll_id):
        # If leave type = 'EL' then
        try:
            t06Lve10_obj = T06Lve10.objects.get(
                employee_code=payroll_id.employee_code,
                actual_date_from__month=payroll_id.payroll_period.pay_month,
                actual_date_from__year=payroll_id.payroll_period.pay_year,
            )
        except T06Lve10.DoesNotExist:
            logger.error(
                "T06Lve10 object doesn't exist for the given employee and payroll period."
            )
            return 0, 0
        encash_days = t06Lve10_obj.find_days(
            t06Lve10_obj.actual_date_to, t06Lve10_obj.actual_date_from
        )
        encash_amount = T06Prl14.encash_lve_amt(payroll_id)
        return encash_days, encash_amount

    def get_leaves_availed(employee_code, leave_code):
        from django.db.models import Sum

        return (
            T06Emp12.objects.filter(employee_code=employee_code, leave_code=leave_code)
            .values("leave_availed")
            .annotate(Sum("leave_availed"))
        )

    def update_t06emp12(payroll_period):
        t06Emp12_objs = T06Emp12.objects.all()
        for t06Emp12_obj in t06Emp12_objs:
            try:
                t06Emp12_obj.leave_accrual = 2.5 * payroll_period.pay_month
                t06Emp12_obj.leave_availed = T06Lve10.availed_days(
                    t06Emp12_obj.leave_code,
                    t06Emp12_obj.employee_code,
                    payroll_period.pay_month,
                    payroll_period.pay_year,
                )
                payroll_id = T06Prl10.objects.get(
                    employee_code=t06Emp12_obj.employee_code,
                    payroll_period=payroll_period,
                )
                t06Emp12_obj.leave_encashed, encash_amount = T06Prl12.lve_encashment(
                    payroll_id
                )
                t06Emp12_obj.leave_clbal = (
                    t06Emp12_obj.leave_opbal
                    + t06Emp12_obj.leave_accrual
                    - t06Emp12_obj.leave_availed
                    - t06Emp12_obj.leave_encashed
                )
                # leave_clbal_date = prl_run_date(). Function written in payroll master class
                t06Emp12_obj.leave_clbal_date = timezone.now()
            except Exception as error:
                logger.error(f"Error during T06Emp12 objects updation: {error} ")
        try:
            T06Emp12.objects.bulk_update(
                t06Emp12_objs,
                [
                    "leave_accrual",
                    "leave_availed",
                    "leave_encashed",
                    "leave_clbal",
                    "leave_clbal_date",
                ],
            )
        except Exception as error:
            logger.error(f"Error during T06Emp12 objects updation: {error} ")


class T06Prl13(models.Model):
    payroll_id = models.ForeignKey(
        T06Prl10, on_delete=models.CASCADE, db_column="IDROLL10", null=True
    )
    employee_allowances = models.ForeignKey(
        T06Emp13, models.PROTECT, db_column="IDEmpAlw", null=True
    )
    alw_unit_qty = models.FloatField(db_column="fAlwUnitQty", default=1)  # manual entry
    project = models.ForeignKey(
        T01Prj10, models.PROTECT, db_column="IDPrlPrj", null=True
    )  # manual entries
    project_alw_amt = models.FloatField(db_column="fPrjAlwAmt", null=True)
    wps_housing_amt = models.FloatField(db_column="fWpHouseamt", blank=True, null=True)
    wps_transport_amt = models.FloatField(
        db_column="fWpTransamt", blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T06PRL13"
        verbose_name = "Payroll Allowance Amount"
        ordering = ("id",)

    def __str__(self):
        return f"{self.employee_allowances}"

    def insert_t06prl13(payroll_period: object):
        t06Prl13_create = []
        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            for t06Emp13_obj in T06Emp13.objects.filter(
                employee_code=payroll_id.employee_code
            ):
                try:
                    t06Prl13_create.append(
                        T06Prl13(
                            payroll_id=payroll_id, employee_allowances=t06Emp13_obj
                        )
                    )
                except Exception as error:
                    logger.error(f"Error in creating T06Prl13 object:{error}")
                    continue
        if t06Prl13_create:
            try:
                T06Prl13.objects.bulk_create(t06Prl13_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl13 bulk objects:{error}")

    def alw_amt(self):
        fa_amt = 0
        va_amt = 0
        try:
            alwamt = self.employee_allowances.allowance_rate * self.alw_unit_qty
            t06Alw10_obj = self.employee_allowances.allowance_code

            if t06Alw10_obj.as_per_days_worked == True:
                alwamt = self.payroll_id.tot_days_worked * (
                    alwamt
                    / T06Prl10.paydays(
                        self.payroll_id.payroll_period.pay_year,
                        self.payroll_id.payroll_period.pay_month,
                    )
                )
            if t06Alw10_obj.allowance_type == "FA":
                fa_amt += alwamt
            if t06Alw10_obj.allowance_type == "VA":
                va_amt += alwamt
            self.project_alw_amt = fa_amt + va_amt
            self.save()
            return fa_amt, va_amt

        except Exception as error:
            logger.error(str(error))
            return -1, -1


class T06Prl14(models.Model):
    payroll_id = models.ForeignKey(
        T06Prl10, on_delete=models.CASCADE, db_column="IDROLL10", null=True
    )
    ticket_rule = models.ForeignKey(
        "T06Tkr10", models.PROTECT, db_column="IDTKR10", null=True
    )
    ticket_paid_amount = models.FloatField(db_column="fTktPaidAmt", null=True)
    encash_amount = models.FloatField(db_column="fTktEncashAmt", null=True)

    class Meta:
        #    managed = False
        db_table = "T06PRL14"
        verbose_name = "Payroll Ticket Amount"
        ordering = ("id",)

    def __str__(self):
        return f"{self.ticket_rule}"

    def insert_t06prl14(payroll_period):
        t06Prl14_create = []
        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            try:
                t06Lve10_obj = T06Lve10.objects.get(
                    employee_code=payroll_id.employee_code,
                    actual_date_from__month=payroll_id.payroll_period.pay_month,
                    actual_date_from__year=payroll_id.payroll_period.pay_year,
                )
                for t06Emp14_obj in T06Emp14.objects.filter(
                    employee_code=payroll_id.employee_code
                ):

                    try:
                        #     Insert record in T06Prl14,
                        t06Prl14_create.append(
                            T06Prl14(
                                # match payroll_id with T06Lve10.employee_code, month, year
                                payroll_id=payroll_id,
                                # read ticket count and ticket amount from T06Emp14
                                ticket_paid_amount=t06Emp14_obj.ticket_count
                                * t06Emp14_obj.ticket_amount,
                                encash_amount=T06Prl14.encash_tkt(),
                            )
                        )

                    except Exception as error:
                        logger.error(f"Error in creating T06Prl14 object:{error}")
                        continue
            except Exception as error:
                logger.error(f"Error in insert_t06prl14:{error}")
                continue
        if t06Prl14_create:
            try:
                T06Prl14.objects.bulk_create(t06Prl14_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl14 bulk objects:{error}")

    def update_t06prl14(payroll_period: object):
        t06Prl14_create, t06Prl14_update = [], []
        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            try:
                t06Lve10_obj = T06Lve10.objects.get(
                    employee_code=payroll_id.employee_code,
                    actual_date_from__month=payroll_id.payroll_period.pay_month,
                    actual_date_from__year=payroll_id.payroll_period.pay_year,
                )
                for t06Emp14_obj in T06Emp14.objects.filter(
                    employee_code=payroll_id.employee_code
                ):

                    try:
                        ticket_paid_amount = (
                            t06Emp14_obj.ticket_count * t06Emp14_obj.ticket_amount
                        )
                        encash_amount = T06Prl14.encash_tkt()
                        queryset = T06Prl14.objects.filter(payroll_id=payroll_id)
                        if queryset.exists():
                            for obj in queryset:
                                obj.ticket_paid_amount = ticket_paid_amount
                                obj.encash_amount = encash_amount
                            t06Prl14_update.extend(queryset)
                        else:
                            t06Prl14_create.append(
                                T06Prl14(
                                    payroll_id=payroll_id,
                                    ticket_paid_amount=ticket_paid_amount,
                                    encash_amount=encash_amount,
                                )
                            )
                            # Update tkt_paid_upto field in t06Emp14
                            t06Emp14_obj.update(tkt_paid_upto=datetime.date.today())

                    except Exception as error:
                        logger.error(f"Error in creating T06Prl14 object:{error}")
                        continue
            except T06Lve10.DoesNotExist:
                logger.error(
                    "T06Lve10 object doesn't exist for the given employee and payroll period."
                )
        if t06Prl14_create:
            try:
                T06Prl14.objects.bulk_create(t06Prl14_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl14 bulk objects:{error}")
                return ValueError("Error while creating payroll ticket amount.")

        if t06Prl14_update:
            try:
                T06Prl14.objects.bulk_update(
                    t06Prl14_update, ["ticket_paid_amount", "encash_amount"]
                )
            except Exception as error:
                logger.error(f"Error during T06Prl14 objects updation: {error} ")
                return ValueError("Error while updating payroll ticket amount.")

    # called by ticket_amt(self) in PRl10
    def prl_ticket_amt(payroll_id):
        # - one object in T06Emp14 per employee
        # if Month(Date_Joined) = payroll month then
        if (
            payroll_id.employee_code.joining_date.month
            == payroll_id.payroll_period.pay_month
        ):
            t06Prl14_objs = T06Prl14.objects.filter(payroll_id=payroll_id)
            if t06Prl14_objs:
                from django.db.models import Sum

                t06Prl14_dict = t06Prl14_objs.values("ticket_paid_amount").annotate(
                    Sum("ticket_paid_amount")
                )
                return t06Prl14_dict[0].get("ticket_paid_amount__sum", None)
        return 0

    def encash_tkt(self):
        encashment = 0
        t06Lve10_obj = T06Lve10.objects.get(employee_code=self.employee_code)
        if t06Lve10_obj.encash_tkt == "Yes":
            try:
                t06Emp14_obj = T06Emp14.objects.get(employee_code=self.employee_code)
            except T06Emp14.DoesNotExist:
                logger.error("T06Emp14 object doesn't exist for the employee.")
                return 0

            if t06Emp14_obj:
                encashment = t06Emp14_obj.ticket_amount
        return encashment

    def encash_lve_amt(self, payroll_id):
        encashment = 0
        t06Lve10_obj = T06Lve10.objects.get(
            employee_code=payroll_id.employee_code,
            actual_date_from__month=payroll_id.payroll_period.pay_month,
            actual_date_from__year=payroll_id.payroll_period.pay_year,
        )
        if payroll_id:
            daily_rate = payroll_id.pay_per_day()
            encashment = (
                T06Lve10.find_days(
                    t06Lve10_obj.actual_date_to, t06Lve10_obj.actual_date_from
                )
                * daily_rate
            )
        return encashment


class T06Prl15(models.Model):
    payroll_id = models.ForeignKey(
        T06Prl10, on_delete=models.CASCADE, db_column="IDROLL10", null=True
    )
    loan_availed = models.ForeignKey(
        T06Emp15, models.PROTECT, db_column="IDEmpLoan", null=True
    )
    loan_emi = models.FloatField(db_column="fEmiAmt", null=True)
    loan_deduction = models.FloatField(
        db_column="fDedNow", null=True
    )  # editable, to allow override
    payroll_rundt = models.DateField(db_column="dtPrlRunDt", null=True)

    class Meta:
        #    managed = False
        db_table = "T06PRL15"
        verbose_name = "Payroll loan EMI"
        verbose_name_plural = "Payroll loan EMI"
        ordering = ("id",)

    def __str__(self):
        return f"{self.loan_availed}"

    def loan_ded(total_net_loan_balance, total_emi_amount, total_last_emi_adjustment):
        emi = 0
        if (
            total_net_loan_balance > 0
            and (total_net_loan_balance - total_emi_amount) >= 0
        ):
            emi += total_emi_amount
        elif total_net_loan_balance > 0:
            emi += total_last_emi_adjustment
        return emi

    def insert_t06prl15(payroll_period):
        t06Prl15_create = []
        from django.db.models import Sum

        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            for t06EMP15_obj in T06Emp15.objects.filter(
                employee_code=payroll_id.employee_code
            ):
                try:
                    net_loan_balance = t06EMP15_obj.net_loan_balance

                    if net_loan_balance > 0:
                        emi_amount = t06EMP15_obj.emi_amount
                        last_emi_adjustment = t06EMP15_obj.last_emi_adjustment
                        loan_deduction = T06Prl15.loan_ded(
                            net_loan_balance, emi_amount, last_emi_adjustment
                        )

                        t06Prl15_create.append(
                            T06Prl15(
                                payroll_id=payroll_id,
                                loan_availed=t06EMP15_obj.loan_amount,
                                loan_emi=emi_amount,
                                loan_deduction=loan_deduction,
                                payroll_rundt=timezone.now(),
                            )
                        )

                except Exception as error:
                    logger.error(f"Error :{error}")
                    return 0

        if t06Prl15_create:
            try:
                T06Prl15.objects.bulk_create(t06Prl15_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl15 bulk objects:{error}")

    def update_t06prl15(payroll_period):
        t06Prl15_create = []
        t06Prl15_update = []
        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            for t06EMP15_obj in T06Emp15.objects.filter(
                employee_code=payroll_id.employee_code
            ):
                try:
                    net_loan_balance = t06EMP15_obj.net_loan_balance
                    if net_loan_balance > 0:

                        emi_amount = t06EMP15_obj.emi_amount
                        last_emi_adjustment = t06EMP15_obj.last_emi_adjustment
                        loan_deduction = T06Prl15.loan_ded(
                            net_loan_balance, emi_amount, last_emi_adjustment
                        )
                        loan_availed = t06EMP15_obj.loan_amount

                        queryset = T06Prl15.objects.filter(payroll_id=payroll_id)

                        if queryset.exists():
                            for obj in queryset:
                                obj.emi_amount = emi_amount
                                obj.last_emi_adjustment = last_emi_adjustment
                                obj.loan_deduction = loan_deduction
                            t06Prl15_update.extend(queryset)

                        else:
                            t06Prl15_create.append(
                                T06Prl15(
                                    payroll_id=payroll_id,
                                    loan_availed=loan_availed,
                                    loan_emi=emi_amount,
                                    loan_deduction=loan_deduction,
                                    payroll_rundt=timezone.now(),
                                )
                            )

                except Exception as error:
                    logger.error(f"Error :{error}")
                    return 0

        if t06Prl15_create:
            try:
                T06Prl15.objects.bulk_create(t06Prl15_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl15 bulk objects:{error}")
        if t06Prl15_update:
            try:
                T06Prl15.objects.bulk_update(
                    t06Prl15_update, ["loan_availed", "loan_emi", "loan_deduction"]
                )
            except Exception as error:
                logger.error(f"Error during T06Prl15 objects updation: {error} ")

    def prl_loan_ded(payroll_id):
        t06Prl15_objs = T06Prl15.objects.filter(payroll_id=payroll_id)
        if t06Prl15_objs:
            from django.db.models import Sum

            t06Prl15_dict = t06Prl15_objs.values("loan_deduction").annotate(
                Sum("loan_deduction")
            )
            return t06Prl15_dict[0].get("loan_deduction__sum", None)
        return 0

    def prl_loan_emi(payroll_id):
        t06Prl15_objs = T06Prl15.objects.filter(payroll_id=payroll_id)
        if t06Prl15_objs:
            from django.db.models import Sum

            t06Prl15_dict = t06Prl15_objs.values("loan_emi").annotate(Sum("loan_emi"))
            return t06Prl15_dict[0].get("loan_emi__sum", None)
        return 0


class T06Prl16(models.Model):
    payroll_id = models.ForeignKey(
        T06Prl10, on_delete=models.CASCADE, db_column="IDROLL10", null=True
    )
    monthly_deduction = models.ForeignKey(
        T06Emp16, models.PROTECT, db_column="IDEmpDed", null=True
    )
    deduction_amount = models.FloatField(
        db_column="fDedAmt", null=True
    )  # editable, override allowed

    class Meta:
        #    managed = False
        db_table = "T06PRL16"
        verbose_name = "Payroll Deduction"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.payroll_id}, {self.monthly_deduction}, {self.deduction_amount}"

    def insert_t06prl16(payroll_period):
        t06Prl16_create = []
        # Insert records from T06EMP16 and update deduction amount from T06EMP16.
        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            for t06Emp16_obj in T06Emp16.objects.filter(
                employee_code=payroll_id.employee_code
            ):
                try:
                    t06Prl16_create.append(
                        T06Prl16(
                            payroll_id=payroll_id,
                            monthly_deduction=t06Emp16_obj,
                            deduction_amount=t06Emp16_obj.deduction_amount,
                        )
                    )
                except Exception as error:
                    logger.error(f"Error in function insert_t06prl16:{error}")
                    return
        if t06Prl16_create:
            try:
                T06Prl16.objects.bulk_create(t06Prl16_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl16 bulk objects:{error}")

    def update_t06prl16(payroll_period):
        t06Prl16_create = []
        t06Prl16_update = []
        for payroll_id in T06Prl10.objects.filter(payroll_period=payroll_period):
            for t06Emp16_obj in T06Emp16.objects.filter(
                employee_code=payroll_id.employee_code
            ):
                try:
                    queryset = T06Prl16.objects.filter(
                        payroll_id=payroll_id, monthly_deduction=t06Emp16_obj
                    )
                    if queryset.exists():
                        for obj in queryset:
                            if obj.deduction_amount != t06Emp16_obj.deduction_amount:
                                obj.deduction_amount = t06Emp16_obj.deduction_amount
                        t06Prl16_update.extend(queryset)
                    else:
                        # Creating new objects
                        t06Prl16_create.append(
                            T06Prl16(
                                payroll_id=payroll_id,
                                monthly_deduction=t06Emp16_obj,
                                deduction_amount=t06Emp16_obj.deduction_amount,
                            )
                        )
                except Exception as error:
                    logger.error(f"Error in insert_t06prl16:{error}")
                    return ValueError("Error in insert payroll deduction.")
        if t06Prl16_create:
            try:
                T06Prl16.objects.bulk_create(t06Prl16_create)
            except Exception as error:
                logger.error(f"Error in creating T06Prl16 bulk objects:{error}")
                return ValueError("Error in creating payroll deduction.")

        if t06Prl16_update:
            try:
                T06Prl16.objects.bulk_update(
                    t06Prl16_update,
                    [
                        "deduction_amount",
                    ],
                )
            except Exception as error:
                logger.error(f"Error during T06Prl16 objects updation: {error} ")
                return ValueError("Error during payroll deduction amount.")

    def prl_deductions(payroll_id):
        t06Prl16_objs = T06Prl16.objects.filter(payroll_id=payroll_id)
        if t06Prl16_objs:
            from django.db.models import Sum

            t06Prl16_dict = t06Prl16_objs.values("deduction_amount").annotate(
                Sum("deduction_amount")
            )
            return t06Prl16_dict[0].get("deduction_amount__sum", None)
        return 0


# Proxy of T06Prs10 for Printing Payroll Checklist
class T06Hrr01(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "d3.Payroll Checklist"


# Proxy of T06Prs10 for Printing Payslip
class T06Hrr02(T06Prs10):
    class Meta:
        proxy = True
        verbose_name = "d4.Payslip"
