import io
import logging
import sys

from django.db import models
from django_countries.fields import CountryField
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from ebos2201.models.m01_core_mas import *
from ebos2206.models.m06_hr_mas import T06Alw10, T06Ded10, T06Doc10, T06Lon10, T06Tkr10

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
pending tasks:
1. Log user actions.. entered, updated, deleted, undeleted, Post, Unposted, Printed, Upload/download
   https://medium.datadriveninvestor.com/monitoring-user-actions-with-logentry-in-django-admin-8c9fbaa3f442
2. History logging in case of update, delete, undelete, post, unpost
   https://django-simple-history.readthedocs.io/
3. verify fieldtypes, foreignkey, db_column naming convention, blank/null allowed
4. write def __str__() functions .... input >> output
"""


class T06Emp10(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("none", "None"),
    )

    STATUS_CHOICES = (
        (1, "Active"),
        (2, "UPS counted"),
        (3, "Not returned"),
        (4, "Resigned"),
        (5, "Terminated"),
        (6, "Others"),
    )

    employee_code = models.CharField(
        db_column="sEmpCode", max_length=10, blank=True, unique=True
    )
    designation = models.ForeignKey(
        T01Dsg10, models.PROTECT, db_column="IDEmpDsg", null=True
    )
    sub_ledger = models.BigIntegerField(db_column="IDSLD10", null=True)
    sub_ledger_type = models.CharField(db_column="sSLType", max_length=2, blank=True)
    first_name = models.CharField(db_column="sNameF", max_length=50)
    last_name = models.CharField(db_column="sNameL", max_length=50)
    middle_name = models.CharField(
        db_column="sNameM", max_length=50, blank=True, null=True
    )
    profile_pic = models.ImageField(
        upload_to="profile_pic/", blank=True, null=True, db_column="bPic"
    )
    gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, default="male", db_column="sGen"
    )
    date_of_birth = models.DateTimeField(db_column="dtDOB", null=True)
    birth_place = models.CharField(db_column="sBirthPlace", max_length=50, blank=True)
    home_country = models.CharField(db_column="sHomeCountry", max_length=50, blank=True)
    primary_address1 = models.CharField(db_column="sAddr1", max_length=60, blank=True)
    primary_address2 = models.CharField(db_column="sAddr2", max_length=50, blank=True)
    primary_address3 = models.CharField(db_column="sAddr3", max_length=50, blank=True)
    father_name = models.CharField(db_column="sNameFA", max_length=50, blank=True)
    mother_name = models.CharField(db_column="sNameMA", max_length=50, blank=True)
    next_of_kin = models.CharField(db_column="sNextKin", max_length=50, blank=True)
    relation = models.CharField(db_column="sRelation", max_length=50, blank=True)
    kin_address1 = models.CharField(db_column="sAddrKin1", max_length=60, blank=True)
    kin_address2 = models.CharField(db_column="sAddrKin2", max_length=50, blank=True)
    kin_address3 = models.CharField(db_column="sAddrKin3", max_length=50, blank=True)
    mobile = models.CharField(db_column="sMob", max_length=25, blank=True)
    residence_phone1 = models.CharField(db_column="sPh1", max_length=25, blank=True)
    residence_phone2 = models.CharField(db_column="sPh2", max_length=25, blank=True)
    email = models.CharField(db_column="sEmail", max_length=50, blank=True)
    others = models.CharField(db_column="sOther", max_length=25, blank=True)
    nationality = CountryField(db_column="IdNationality", null=True)
    categories = models.ManyToManyField(T01Cat10, db_column="IDEmpCat", blank=True)
    basic_pay = models.FloatField(
        db_column="fBasic",
        default="0.00",
    )
    working_hr_per_day = models.FloatField(db_column="dWorkHr", default="8.0")
    joining_date = models.DateTimeField(db_column="dtJoin")
    rejoin_date = models.DateTimeField(db_column="dtRejoin", blank=True, null=True)
    employee_status = models.IntegerField(
        db_column="nStatus", choices=STATUS_CHOICES, default=1
    )
    date_of_status = models.DateTimeField(db_column="dtSTS", null=True)
    date_of_cancel = models.DateTimeField(db_column="dtCancel", blank=True, null=True)
    cancel_reason = models.CharField(
        db_column="sCancelReason", max_length=50, blank=True
    )
    date_last_payroll = models.DateField(db_column="dPayrollRun", blank=True, null=True)
    emp_file_ref = models.CharField(db_column="sFile", max_length=50, blank=True)
    emp_wps_uid = models.CharField(db_column="sEmpUID", max_length=15, blank=True)

    class Meta:
        #    managed = False
        db_table = "T06EMP10"
        ordering = ["employee_code"]
        verbose_name = "a8.Employee Master"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_code})"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if not self.employee_code:
            T06Emp10.objects.filter(id=self.id).update(employee_code=f"{self.id:04d}")


# employee bank accounts
class T06Emp11(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        db_column="IDemployee",
        on_delete=models.CASCADE,
        related_name="bank_acct_set",
    )
    bank_name = models.CharField(db_column="sBnkName", max_length=50, blank=True)
    beneficiery = models.CharField(db_column="Beneficiery", max_length=50, blank=True)
    bank_acc = models.CharField(db_column="sACNo", max_length=50, blank=True)
    bank_iban = models.CharField(db_column="sIBAN", max_length=50, blank=True)
    bank_swift_code = models.CharField(
        db_column="sSWIFTcode", max_length=20, blank=True
    )
    active_flag = models.BooleanField(db_column="bActive", default=True)
    wps_agent_code = models.CharField(
        db_column="sWpsBankCode", max_length=15, blank=True
    )
    active_flag = models.BooleanField(db_column="bActive", default=True)

    class Meta:
        db_table = "T06EMP11"
        verbose_name = "Employee Bank Acct"
        ordering = ["employee_code__employee_code"]

    def __str__(self) -> str:
        return f"{self.bank_name} ({self.employee_code})"


class T06Emp12(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        db_column="IDemployee",
        null=True,
        on_delete=models.CASCADE,
        related_name="emp_leave_set",
    )
    leave_code = models.ForeignKey(
        "T06Lvr10", models.PROTECT, db_column="sLveCode", null=True
    )
    leave_opbal_date = models.DateTimeField(
        db_column="dtLveObal", blank=True, null=True
    )
    leave_opbal = models.FloatField(db_column="fLveObal", blank=True, null=True)
    leave_accrual = models.FloatField(db_column="fLveAccrual", blank=True, null=True)
    leave_availed = models.FloatField(db_column="fLveAvailed", blank=True, null=True)
    leave_encashed = models.FloatField(db_column="nLveEncashed", blank=True, null=True)
    leave_clbal = models.FloatField(db_column="fLveClBal", blank=True, null=True)
    leave_clbal_date = models.DateTimeField(
        db_column="dtLveClbal", blank=True, null=True
    )
    leave_write_off = models.FloatField(db_column="fLveWrtOff", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T06EMP12"
        verbose_name = "Employee Leave Record"
        ordering = ["employee_code__employee_code"]

    def __str__(self) -> str:
        return f"{self.employee_code} - {self.leave_code} - {self.leave_availed} - {self.leave_clbal}"


class T06Emp13(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        db_column="IDemployee",
        null=True,
        on_delete=models.CASCADE,
        related_name="emp_allow_set",
    )
    allowance_code = models.ForeignKey(
        T06Alw10, models.PROTECT, db_column="IDALW10", null=True
    )
    allowance_rate = models.FloatField(db_column="falwRate", null=True)
    ALW_UNITS = (("M", "Monthly"), ("D", "Daily"), ("H", "Hourly"))
    allowance_unit = models.CharField(
        db_column="sAlwUnit", max_length=1, choices=ALW_UNITS, default="M"
    )
    wps_housing = models.BooleanField(db_column="bWpHouse", default=False)
    wps_transport = models.BooleanField(db_column="bWpTrans", default=False)

    class Meta:
        #    managed = False
        db_table = "T06EMP13"
        verbose_name = "Employee Allowance Record"
        ordering = ["employee_code__employee_code"]

    def __str__(self):
        return "%s [%s]" % (self.allowance_rate, self.get_allowance_unit_display())


# previously T06Psg10
class T06Emp14(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        db_column="IDemployee",
        null=True,
        on_delete=models.CASCADE,
        related_name="emp_tic_set",
    )
    ticket_rule = models.ForeignKey(
        T06Tkr10, models.PROTECT, db_column="IDTKR10", null=True
    )
    home_country = models.CharField(db_column="sHomeCountry", max_length=50, blank=True)
    ticket_count = models.FloatField(db_column="fTickQty", null=True)
    ticket_amount = models.FloatField(db_column="fTickVal", null=True)
    tkt_paid_upto = models.DateField(db_column="dTktPaidUpto", null=True, blank=True)

    class Meta:
        #    managed = False
        db_table = "T06EMP14"
        verbose_name = "Employee Ticket Record"
        ordering = ["employee_code__employee_code"]

    def __str__(self) -> str:
        return f"{self.ticket_rule}"


# previously T06Lon11
class T06Emp15(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        on_delete=models.CASCADE,
        db_column="IDemployee",
        null=True,
        related_name="emp_loan_set",
    )
    loan_type = models.ForeignKey(
        T06Lon10, models.PROTECT, db_column="IDLON10", null=True
    )
    loan_amount = models.FloatField(db_column="fLoanAmt", null=True)
    no_of_emi = models.IntegerField(db_column="fEmiTenure", null=True)
    emi_amount = models.IntegerField(db_column="fEmiAmt", null=True)
    last_emi_adjustment = models.FloatField(db_column="fLastEmiAdj", null=True)
    total_loan_deduction = models.FloatField(db_column="fTotLoanDed", null=True)
    net_loan_balance = models.FloatField(db_column="fLoanBal", null=True)
    deduction_start_date = models.DateTimeField(db_column="dtDedFrom", null=True)
    deduction_asof_date = models.DateTimeField(
        db_column="dtDedAsOf", blank=True, null=True
    )
    loan_ref = models.CharField(db_column="sLONref", max_length=20, blank=True)

    class Meta:
        #    managed = False
        db_table = "T06EMP15"
        verbose_name = "Employee Loan Record"
        ordering = ["employee_code__employee_code"]

    def loan_update():
        #  total_loan_deduction += T06Prl15.loan_deduction
        #  net_loan_balance = loan_amount - total_loan_deduction
        #  deduction_asof_date = T06Prl15.payroll_rundt
        pass

    def __str__(self):
        return f"{self.loan_type} - {self.loan_amount}"


class T06Emp16(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        on_delete=models.CASCADE,
        db_column="IDEMP10",
        null=True,
        related_name="emp_deduc_set",
    )
    deduction_code = models.ForeignKey(
        T06Ded10, models.PROTECT, db_column="IDDED10", null=True
    )
    deduction_amount = models.FloatField(db_column="fAmt", null=True)

    class Meta:
        #    managed = False
        db_table = "T06EMP16"
        verbose_name = "Employee Deductions Record"
        ordering = ["employee_code__employee_code"]

    def __str__(self):
        return f"{self.deduction_code} - {self.deduction_amount}"


class T06Emp17(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        on_delete=models.CASCADE,
        db_column="IDemployee",
        null=True,
        related_name="emp_ass_set",
    )
    asset_ref = models.BigIntegerField(db_column="IDFAM10", null=True)
    dt_of_issue = models.DateTimeField(db_column="dtIssued", null=True)
    dt_of_return = models.DateTimeField(db_column="dtReturned", blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "T06EMP17"
        verbose_name = "Employee Asset Record"
        ordering = ["employee_code__employee_code"]

    def __str__(self) -> str:
        return f"{self.employee_code} - {self.asset_ref}"


class T06Emp18(models.Model):
    employee_code = models.ForeignKey(
        T06Emp10,
        on_delete=models.CASCADE,
        db_column="IDemployee",
        null=True,
        related_name="emp_doc_set",
    )
    document_name = models.ForeignKey(
        T06Doc10, models.PROTECT, db_column="IDDOC10", null=True
    )
    attachment = models.FileField(
        upload_to="documents/emp_master/", db_column="uEmpDocs", null=True
    )
    document_no = models.CharField(db_column="sDocNo", max_length=25, blank=True)
    dt_of_issue = models.DateTimeField(db_column="dtIssue", blank=True, null=True)
    dt_of_expiry = models.DateTimeField(db_column="dtExpiry", blank=True, null=True)
    place_of_issue = models.CharField(
        db_column="sIssuePlace", max_length=50, blank=True
    )
    ref1 = models.CharField(db_column="sRef1", max_length=25, blank=True)
    ref2 = models.CharField(db_column="sRef2", max_length=25, blank=True)

    class Meta:
        #    managed = False
        db_table = "T06EMP18"
        verbose_name = "Employee Documents Record"
        ordering = ["employee_code__employee_code"]

    def __str__(self) -> str:
        return f"{self.employee_code} - {self.document_name}"


class T06Dex10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDDivEml", null=True
    )
    department = models.ForeignKey(
        T01Dep10, models.PROTECT, db_column="IDDepEml", blank=True, null=True
    )
    document_type = models.ForeignKey(
        T06Doc10, models.PROTECT, db_column="IDDocEml", null=True, blank=True
    )
    date_from = models.DateField(db_column="dFrom", null=True)
    date_to = models.DateField(db_column="dTo", null=True)
    report_file = models.FileField(
        upload_to="",
        max_length=250,
        null=True,
        db_column="fReport",
        blank=True,
        default=None,
    )
    email_code = models.ForeignKey(
        T01Atm10, models.PROTECT, db_column="IDAtmCode", null=True, blank=True
    )

    class Meta:
        db_table = "T06DEX10"
        verbose_name = "d1.Document Expiry Report"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.division} - {self.department}"

    def emp_doc_exp_report(data):
        buffer = io.BytesIO()
        fileobj = canvas.Canvas(buffer, pagesize=(landscape(A4)))
        date_from = data.date_from
        date_to = data.date_to

        # Filter on the basis of doc_type, department and division
        if (data.department) and (data.division) and (data.document_type):
            getData_T06Emp18 = T06Emp18.objects.filter(
                document_name=data.document_type,
                employee_code__designation__department=data.department,
                employee_code__designation__department__division=data.division,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )

        elif not (data.department) and (data.division) and (data.document_type):
            getData_T06Emp18 = T06Emp18.objects.filter(
                document_name=data.document_type,
                employee_code__designation__department__division=data.division,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )

        elif (data.department) and not (data.division) and (data.document_type):
            getData_T06Emp18 = T06Emp18.objects.filter(
                document_name=data.document_type,
                employee_code__designation__department=data.department,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )

        elif (data.department) and (data.division) and not (data.document_type):
            getData_T06Emp18 = T06Emp18.objects.filter(
                employee_code__designation__department=data.department,
                employee_code__designation__department__division=data.division,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )

        elif not (data.department) and not (data.division) and (data.document_type):
            getData_T06Emp18 = T06Emp18.objects.filter(
                document_name=data.document_type,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )

        elif (data.department) and not (data.division) and not (data.document_type):
            getData_T06Emp18 = T06Emp18.objects.filter(
                employee_code__designation__department=data.department,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )
        else:
            getData_T06Emp18 = T06Emp18.objects.filter(
                employee_code__designation__department__division=data.division,
                dt_of_expiry__date__gte=date_from,
                dt_of_expiry__date__lte=date_to,
            )

        Sr_no = 0
        table_data = [
            [
                "S.No.",
                "Emp#",
                "Name",
                "Doc. Type",
                "Doc. ref",
                "Expiry dt.",
                "Issue dt.",
                "Place of issue",
                "Ref1",
                "Ref2",
            ]
        ]
        if getData_T06Emp18.exists():
            for obj in getData_T06Emp18:
                Sr_no = Sr_no + 1
                employee_code = obj.employee_code.employee_code
                employee_name = (
                    obj.employee_code.first_name
                    + " "
                    + obj.employee_code.middle_name
                    + " "
                    + obj.employee_code.last_name
                )
                doc_type = data.document_type.document_name
                document_ref = obj.document_no
                dt_of_issue = str(obj.dt_of_issue.date())
                dt_of_expiry = str(obj.dt_of_expiry.date())
                place_of_issue = obj.place_of_issue
                Ref1 = obj.ref1
                Ref2 = obj.ref2
                data_list = [
                    Sr_no,
                    employee_code,
                    employee_name,
                    doc_type,
                    document_ref,
                    dt_of_issue,
                    dt_of_expiry,
                    place_of_issue,
                    Ref1,
                    Ref2,
                ]
                table_data.append(data_list)

        else:
            fileobj.setFont("Helvetica-Bold", 11)
            fileobj.drawString(300, 380, "No Record Found")

        fileobj.setFont("Helvetica-Bold", 16)
        fileobj.drawString(40, 560, data.division.company.company_name)
        fileobj.setFont("Helvetica", 11)
        fileobj.drawString(550, 560, "Report: " + "Document Renewal")
        fileobj.setFont("Helvetica", 11)
        fileobj.drawString(40, 540, data.division.company.company_location)
        fileobj.setFont("Helvetica", 11)
        fileobj.drawString(
            550, 540, "Date Range: " + str(date_from) + " to " + str(date_to)
        )
        width = 1000
        height = 100
        borderStyle = "solid"
        x = 40
        y = 400
        f = Table(table_data)
        f.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )
        f._argW[3] = 3.0 * inch
        f.wrapOn(fileobj, width, height)
        f.drawOn(fileobj, x, y)

        fileobj.showPage()
        fileobj.save()
        buffer.seek(0)
        return buffer
