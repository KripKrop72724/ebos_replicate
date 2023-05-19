from django.db import models

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2201.validators import validate_month, validate_year

from .m06_emp_mas import T06Emp10, T06Emp11
from .m06_prl_trn import *


class T06Exc10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    claim_cat = models.ForeignKey(
        T01Cat10, models.PROTECT, db_column="sClaimCat", blank=True, null=True
    )
    gl_code = models.IntegerField(db_column="nExcGLCode", null=True, blank=True)
    claim_date = models.DateField(db_column="dtExpClaim", null=True)
    claim_note = models.TextField(db_column="sClaimNote", blank=True)
    claim_amount = models.FloatField(db_column="fClaimAmt", null=True)
    CLAIM_STATUS = (
        ("1", "Pending"),
        ("2", "Processing"),
        ("3", "Paid"),
        ("4", "Rejected"),
    )
    claim_status = models.CharField(
        db_column="sClaimStatus", max_length=1, choices=CLAIM_STATUS, default="1"
    )
    claim_approver = models.ForeignKey(
        T06Emp10,
        models.PROTECT,
        related_name="excapprover",
        db_column="IDExcAprv",
        blank=True,
        null=True,
    )
    approver_note = models.TextField(db_column="sAprvNote", blank=True)
    date_approved = models.DateField(db_column="dtExcApproved", blank=True, null=True)
    bill_copy = models.FileField(
        upload_to="documents/exp_claim/", blank=True, default=None
    )

    class Meta:
        db_table = "T06EXC10"
        verbose_name = "c2.Employee Expense Claim"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.employee_code} - {self.claim_cat}"

    def post_exp_claims():  # for future use, next version coding
        pass


# Proxy of T06Exc10 for Self Services Expense Claim
class T06Ess02(T06Exc10):
    class Meta:
        proxy = True
        verbose_name = "Self Service Expense Claim"


class T06Hdt10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    service_request = models.TextField(db_column="sSrvRequest", blank=True)
    dt_of_request = models.DateField(db_column="dRequested", null=True)
    SERVICE_STATUS = (("1", "Pending"), ("2", "Processing"), ("3", "Closed"))
    service_status = models.CharField(
        db_column="sSrvStatus", max_length=1, choices=SERVICE_STATUS, default="1"
    )
    service_due_date = models.DateField(db_column="dSrvDue", blank=True, null=True)
    service_note = models.TextField(db_column="sSrvNote", blank=True)
    serviced_by = models.ForeignKey(
        T06Emp10,
        models.PROTECT,
        related_name="servicedby",
        db_column="IDSrvBy",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "T06HDT10"
        verbose_name = "c3.Help Desk Ticket"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.employee_code} ({self.service_request})"


# Proxy of T06Hdt10 for Self Services Help Desk
class T06Ess03(T06Hdt10):
    class Meta:
        proxy = True
        verbose_name = "Self Service Help Desk"


# previously T06NOT10 (notification), changed to Memo
class T06Mem10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        models.PROTECT,
        db_column="IDemployee",
        related_name="memtoemp",
        null=True,
    )
    memo_ref_no = models.CharField(db_column="sMemoRefNo", max_length=10, blank=True)
    memo_type = models.CharField(db_column="sMemoType", max_length=10, blank=True)
    memo_count = models.IntegerField(db_column="nMemoCount", null=True)
    memo_text = models.TextField(db_column="sMemoText", blank=True)
    issued_by = models.ForeignKey(
        T06Emp10,
        models.PROTECT,
        db_column="IDMemIssued",
        related_name="memissuedby",
        null=True,
    )
    authorized_by = models.ForeignKey(
        T06Emp10,
        models.PROTECT,
        db_column="IDMemAuth",
        related_name="memauthorized",
        null=True,
    )
    acknowledged = models.BooleanField(db_column="bAcknowledged", default=False)
    feedback = models.TextField(db_column="sFeedback", blank=True)

    class Meta:
        db_table = "T06MEM10"
        verbose_name = "c4.Employee Memo"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.employee_code} ({self.memo_ref_no})"


# Proxy of T06Mem10 for Self Services Employee Memo
class T06Ess04(T06Mem10):
    class Meta:
        proxy = True
        verbose_name = "Self Service Memo"


class T06Wps10(models.Model):
    wps_year = models.IntegerField(
        db_column="nYear", null=True, validators=validate_year()
    )
    wps_month = models.IntegerField(
        db_column="nMonth", null=True, validators=validate_month()
    )
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column="IDWpsDiv")
    com_record_type = models.CharField(
        db_column="sComWpsCode", max_length=3, blank=True
    )
    com_UID = models.CharField(db_column="sComUID", max_length=15, blank=True)
    com_bnk_name = models.ForeignKey(
        T01Bnk10, models.PROTECT, db_column="IDBnkWps", null=True
    )
    com_bnk_routing_code = models.CharField(
        db_column="sComWpsBnk", max_length=3, blank=True
    )
    file_creation_dt = models.DateTimeField(
        db_column="dtWpsCreated", blank=True, null=True
    )
    sal_record_count = models.IntegerField(
        db_column="nWpsLineCount", blank=True, null=True
    )
    tot_sal_amount = models.FloatField(db_column="fTotSalAmt", blank=True, null=True)
    pay_curr = models.CharField(db_column="sPayCurr", max_length=3, blank=True)
    com_ref_note = models.CharField(db_column="sComRef", max_length=3, blank=True)
    sif_file_name = models.FileField(
        upload_to="wps_reports",
        max_length=250,
        null=True,
        db_column="fSIFFile",
        blank=True,
        default=None,
    )

    class Meta:
        #    managed = False
        db_table = "T06WPS10"
        verbose_name = "d2.WPS sif file"
        ordering = (
            "-wps_year",
            "-wps_month",
        )

    def __str__(self) -> str:
        return f"{self.division}, {self.wps_month}-{self.wps_year}"

    def get_wps_com_data(data):
        # Update T06Wps10
        T06Wps10.objects.filter(id=data.id).update(
            pay_curr=data.division.currency.currency_code,
            com_bnk_name=data.division.wps_bank_code,
            com_bnk_routing_code=T01Bnk10.objects.get(
                division=data.division
            ).wps_routing_code,
            com_record_type="SCR",
            com_UID=data.division.wps_mol_uid,
        )


class T06Wps11(models.Model):
    wps_header = models.ForeignKey(
        T06Wps10,
        models.PROTECT,
        db_column="IdWps10",
        null=True,
        related_name="wps_header_set",
    )
    emp_record_type = models.CharField(
        db_column="sComWpsCode", max_length=3, blank=True
    )
    emp_prl_id = models.ForeignKey(
        T06Prl10, models.PROTECT, db_column="IdWpsPrl", null=True
    )
    emp_UID = models.CharField(db_column="sempWpsUID", max_length=50, blank=True)
    emp_name = models.CharField(db_column="sempWpsName", max_length=50, blank=True)
    emp_bnk_id = models.ForeignKey(
        T01Bnk10, models.PROTECT, db_column="IdEmpWpsBnk", null=True
    )
    emp_Bnk_acct = models.CharField(db_column="sEmpBnkAcc", max_length=50, blank=True)
    sal_fixed_amt = models.FloatField(db_column="fwpsfixedAmt", blank=True, null=True)
    sal_Variable_amt = models.FloatField(db_column="fwpsVarAmt", blank=True, null=True)
    emp_lve_days = models.FloatField(db_column="fwpsLveDays", blank=True, null=True)
    emp_housing_alw = models.FloatField(db_column="fwpsHRAamt", blank=True, null=True)
    emp_transport_alw = models.FloatField(db_column="fwpsTRAamt", blank=True, null=True)
    emp_medical_alw = models.FloatField(db_column="fwpsMLamt", blank=True, null=True)
    emp_tkt_amt = models.FloatField(db_column="fwpsTktAmt", blank=True, null=True)
    emp_ot_amt = models.FloatField(db_column="fwpsOTamt", blank=True, null=True)
    emp_other_alw = models.FloatField(db_column="fwpsOtherAmt", blank=True, null=True)
    emp_lve_encashment = models.FloatField(
        db_column="fwpsLveEncAmt", blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T06WPS11"
        verbose_name = "WPS Detail"

    # Add property net_pay = prl10 netpay
    # validation sum of all amt in wps11 and then it's equal to prl10 netpay
    # if not equal warning : net pay in WPS is not equal to Payroll Net amount
    @property
    def net_pay(self):
        np = (
            (self.sal_fixed_amt if self.sal_fixed_amt else 0)
            + (self.sal_Variable_amt if self.sal_Variable_amt else 0)
            + (self.emp_housing_alw if self.emp_housing_alw else 0)
            + (self.emp_housing_alw if self.emp_housing_alw else 0)
            + (self.emp_transport_alw if self.emp_transport_alw else 0)
            + (self.emp_medical_alw if self.emp_medical_alw else 0)
            + (self.emp_tkt_amt if self.emp_tkt_amt else 0)
            + (self.emp_ot_amt if self.emp_ot_amt else 0)
            + (self.emp_other_alw if self.emp_other_alw else 0)
            + (self.emp_lve_encashment if self.emp_lve_encashment else 0)
        )
        get_T06Prl10 = T06Prl10.objects.filter(id=self.emp_prl_id.id).first()
        T06Prl10_netPay = get_T06Prl10.netpay or 0
        if np != T06Prl10_netPay:
            warn_message = "Net Pay in WPS is not equal to Payroll Net amount"
        else:
            warn_message = "Net Pay in WPS is equal to Payroll Net amount"
        return np, warn_message

    def get_wps_emp_data(data):
        division = data.division
        emp_record_type = "EDR"

        for emp_detail in T06Emp10.objects.all():
            emp_UID = emp_detail.emp_wps_uid
            emp_name = f"{emp_detail.first_name} {emp_detail.middle_name} {emp_detail.last_name}"
            emp_bank_details = T06Emp11.objects.filter(employee_code=emp_detail).first()
            if emp_bank_details != None:
                emp_bnk_acct = emp_bank_details.bank_acc
            else:
                emp_bnk_acct = ""

            get_T06Prl10 = T06Prl10.objects.filter(
                employee_code=emp_detail,
                payroll_period__pay_year=data.wps_year,
                payroll_period__pay_month=data.wps_month,
                payroll_period__division=data.division,
            ).first()
            check_T06Wps11 = T06Wps11.objects.filter(emp_prl_id=get_T06Prl10)

            if not check_T06Wps11:
                record_count, tot_sal_amount = 0, 0

                if get_T06Prl10:
                    sal_fixed_amt = get_T06Prl10.basic_pay + get_T06Prl10.fixed_alw
                    sal_Variable_amt = get_T06Prl10.variable_alw
                    emp_lve_days = (get_T06Prl10.tot_ML_days or 0) + (
                        get_T06Prl10.tot_EL_days or 0
                    )
                    emp_medical_alw = get_T06Prl10.ml_pay
                    emp_tkt_amt = get_T06Prl10.tkt_pay
                    emp_housing_alw = get_T06Prl10.wps_housing_amt
                    emp_transport_alw = get_T06Prl10.wps_transport_amt
                    emp_ot_amt = get_T06Prl10.ot_pay
                    emp_other_alw = get_T06Prl10.other_pay
                    emp_lve_encashment = get_T06Prl10.el_pay
                    wps_header = T06Wps10.objects.get(id=data.id)
                    emp_bnk_id = T01Bnk10.objects.get(division=division)
                    # Create record in T06Wps11
                    T06Wps11_obj = T06Wps11.objects.create(
                        wps_header=wps_header,
                        emp_record_type=emp_record_type,
                        emp_prl_id=get_T06Prl10,
                        emp_UID=emp_UID,
                        emp_name=emp_name,
                        emp_bnk_id=emp_bnk_id,
                        emp_Bnk_acct=emp_bnk_acct,
                        sal_fixed_amt=sal_fixed_amt,
                        sal_Variable_amt=sal_Variable_amt,
                        emp_lve_days=emp_lve_days,
                        emp_medical_alw=emp_medical_alw,
                        emp_tkt_amt=emp_tkt_amt,
                        emp_housing_alw=emp_housing_alw,
                        emp_transport_alw=emp_transport_alw,
                        emp_ot_amt=emp_ot_amt,
                        emp_other_alw=emp_other_alw,
                        emp_lve_encashment=emp_lve_encashment,
                    )
                    netpay_amount, warn_message = T06Wps11_obj.net_pay
                    tot_sal_amount = tot_sal_amount + netpay_amount
                    if sal_fixed_amt > 0:
                        record_count = record_count + 1

                #  Update values in T06Wps10
                sal_record_count = record_count
                tot_sal_amount = tot_sal_amount
                T06Wps10.objects.filter(id=data.id).update(
                    sal_record_count=sal_record_count, tot_sal_amount=tot_sal_amount
                )
        return True


class T06Eos10(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10, models.PROTECT, db_column="IDemployee", null=True
    )
    gratuity_days = models.FloatField(db_column="fGratdays", null=True)
    gratuity_note = models.TextField(db_column="sGratNote", blank=True)
    gratuity_amount = models.FloatField(db_column="fGratAmt", null=True)
    el_days = models.FloatField(db_column="fELDays", null=True)
    el_note = models.TextField(db_column="sELnote", blank=True)
    el_amount = models.FloatField(db_column="fELAmt", null=True)
    loan_balance_amount = models.FloatField(db_column="fLoanBalAmt", null=True)
    ticket_amount = models.FloatField(db_column="fTktAmt", null=True)
    pending_pay = models.FloatField(db_column="fPendingPay", null=True)
    pending_deduction = models.FloatField(db_column="fPendingDed", null=True)
    eos_note = models.TextField(db_column="sEOSpayNote", blank=True)
    gl_code = models.IntegerField(db_column="nEosGlcode", null=True, blank=True)
    post_flag = models.BooleanField(db_column="bPosted", default=False)
    print_EOS = models.FileField(
        upload_to="EOS",
        max_length=250,
        null=True,
        db_column="flprtEos",
        blank=True,
        default=None,
    )

    class Meta:
        db_table = "T06EOS10"
        verbose_name = "End of Service"
        verbose_name_plural = "b9.End of Service"

    def __str__(self) -> str:
        return f"{self.employee_code} ({self.gratuity_days})"

    def insert_T06Eos10(data):
        try:
            employee = data.employee_code
            employment_days = (
                (employee.date_of_cancel - employee.joining_date).days
                if employee.date_of_cancel and employee.joining_date
                else 0
            )
            employment_years = employment_days / 365
            employment_years = 3
            division = employee.department.division
            # A, B, C = 0
            A, B, C = [0, 0, 0]
            x, y, z = [0, 0, 0]

            if employment_years > 1:
                if 1 <= employment_years < 3:
                    get_T06Cfg10 = T06Cfg10.objects.filter(division=division).first()
                    if (
                        get_T06Cfg10
                        and get_T06Cfg10.gratuity_days_1to3yr
                        and employee.basic_pay
                    ):
                        A = get_T06Cfg10.gratuity_days_1to3yr * employee.basic_pay
                        x = get_T06Cfg10.gratuity_days_1to3yr

                if 3 <= employment_years < 5:
                    get_T06Cfg10 = T06Cfg10.objects.filter(division=division).first()
                    if (
                        get_T06Cfg10
                        and get_T06Cfg10.gratuity_days_3to5yr
                        and employee.basic_pay
                    ):
                        B = get_T06Cfg10.gratuity_days_3to5yr * employee.basic_pay
                        y = get_T06Cfg10.gratuity_days_3to5yr

                if employment_years >= 5:
                    get_T06Cfg10 = T06Cfg10.objects.filter(division=division).first()
                    if (
                        get_T06Cfg10
                        and get_T06Cfg10.gratuity_days_3to5yr
                        and employee.basic_pay
                    ):
                        C = get_T06Cfg10.gratuity_days_5yrplus * employee.basic_pay
                        z = get_T06Cfg10.gratuity_days_5yrplus

            gratuity = A + B + C
            gratuity_days = x + y + z
            get_T06Prl10 = T06Prl10.objects.filter(employee_code=employee.id).first()
            if get_T06Prl10:
                payroll_period = get_T06Prl10.payroll_period
                pay_per_day = employee.basic_pay + T06Prl10.alw_pay(
                    get_T06Prl10
                ) / T06Prl10.paydays(payroll_period.pay_year, payroll_period.pay_month)
                el_pay = (
                    T06Emp12.objects.get(employee_code=employee.id).leave_clbal
                    * pay_per_day
                )

            loan_balance_amount = T06Emp15.objects.get(
                employee_code=employee.id
            ).net_loan_balance
            obj_T06Emp14 = T06Emp14.objects.get(employee_code=employee.id)
            tkt_paid_upto = obj_T06Emp14.tkt_paid_upto
            date_cancel = employee.date_of_cancel
            date_last_payroll = employee.date_last_payroll
            if date_cancel - tkt_paid_upto >= 365:
                ticket_amount = obj_T06Emp14.ticket_count * obj_T06Emp14.ticket_amount
            else:
                ticket_amount = 0

            pending_paydays = (date_cancel - date_last_payroll).days
            pay_amount = pending_paydays * pay_per_day
            allw_pay = (T06Prl10.alw_pay(get_T06Prl10) / 30) * pending_paydays
            deductions = (
                T06Prl10.prl_deductions(payroll_period) / 30
            ) * pending_paydays
            pending_pay = pay_amount + allw_pay - deductions

            T06Eos10.objects.filter(data.id).update(
                gratuity_amount=gratuity,
                el_amount=el_pay,
                loan_balance_amount=loan_balance_amount,
                ticket_amount=ticket_amount,
                pending_pay=pending_pay,
                gratuity_days=gratuity_days,
            )
        except Exception as e:
            print(e)
