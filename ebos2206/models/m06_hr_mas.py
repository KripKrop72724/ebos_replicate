from django.db import models

from ebos2201.models.m01_core_mas import T01Dep10, T01Div10


class T06Cfg10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdDivCfg", null=True
    )
    net_roundoff = models.IntegerField(db_column="nRnd", null=True)
    max_working_hrs = models.IntegerField(
        db_column="nMaxWrkHrs", blank=True, null=True
    )  # beyond this OT may be booked
    add_EL_ML_for_netpay = models.BooleanField(
        db_column="bAddELML4NetPay", default=False
    )
    PPD_CHOICES = (
        ("A", "Average 30 days"),
        ("M", "Days in a Month"),
        ("Y", "By 365 days"),
    )
    pay_perday_div = models.CharField(
        db_column="sPPDdivider", max_length=1, choices=PPD_CHOICES, default="A"
    )
    gratuity_days_1to3yr = models.IntegerField(
        db_column="nGratuity1to3", blank=True, null=True
    )
    gratuity_days_3to5yr = models.IntegerField(
        db_column="nGratuity3to5", blank=True, null=True
    )
    gratuity_days_5yrplus = models.IntegerField(
        db_column="nGratuity5plus", blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T06CFG10"
        verbose_name = "a1.HRMS Configuration"

    def __str__(self) -> str:
        return f"{self.division} - {self.net_roundoff}"


class T06Alw10(models.Model):
    allowance_name = models.CharField(db_column="sAlwName", max_length=50, blank=True)
    allowance_code = models.CharField(db_column="sAlwCode", max_length=5, blank=True)
    ALW_CHOICE = (("FA", "Fixed Allowance"), ("VA", "Variable Allowance"))
    allowance_type = models.CharField(
        db_column="sAlwType", max_length=2, choices=ALW_CHOICE, default="FA"
    )
    as_per_days_worked = models.BooleanField(
        db_column="bAsPerWrkDays", default=False
    )  # proportionate to days workedv(Y?N)
    variable_amount_per_mnt = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    gl_code = models.IntegerField(db_column="nAlwGLCode", blank=True, null=True)

    class Meta:
        db_table = "T06ALW10"
        verbose_name = "a2.Allowance Master"
        ordering = ["allowance_name"]

    def __str__(self) -> str:
        return self.allowance_name


class T06Ded10(models.Model):
    deduction_name = models.CharField(db_column="sDedName", max_length=50, blank=True)
    deduction_code = models.CharField(db_column="sDedCode", max_length=5, blank=True)
    gl_code = models.IntegerField(db_column="nDedGLCode", blank=True, null=True)

    class Meta:
        db_table = "T06DED10"
        verbose_name = "a3.Deduction Master"

    def __str__(self) -> str:
        return self.deduction_name


class T06Lon10(models.Model):
    loan_type = models.CharField(db_column="sName", max_length=50, blank=True)
    loan_code = models.CharField(db_column="sCode", max_length=10, blank=True)
    gl_code = models.IntegerField(db_column="nLonGLCode", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T06LON10"
        verbose_name = "a4.Loan Master"

    def __str__(self) -> str:
        return self.loan_type


class T06Doc10(models.Model):
    document_name = models.CharField(db_column="sDocName", max_length=50, blank=True)

    class Meta:
        db_table = "T06DOC10"
        verbose_name = "a5.Type of Document"

    def __str__(self) -> str:
        return self.document_name


class T06Lvr10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDLvrDiv", null=True
    )
    leave_code = models.CharField(db_column="sLveCode", max_length=2, blank=True)
    leave_name = models.CharField(db_column="sLveName", max_length=10, blank=True)
    days_allowed = models.FloatField(db_column="fDayPerm", null=True)
    days_eligible = models.IntegerField(db_column="fElig", null=True)
    days_with_pay = models.FloatField(db_column="fDaysWPay", null=True)
    carryfwd_leave = models.BooleanField(db_column="bCarryForward", null=True)
    encash_leave = models.BooleanField(db_column="bEncash", null=True)
    gl_code = models.IntegerField(db_column="nLvrGLCode", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T06LVR10"
        verbose_name = "a6.Leave Rule"

    def __str__(self):
        return f"{self.leave_name} [{self.leave_code}]"


class T06Tkr10(models.Model):
    department = models.ForeignKey(
        T01Dep10, models.PROTECT, db_column="IDTkrDep", null=True
    )
    ticket_cycle = models.FloatField(
        db_column="fTktCycle", default=12
    )  # Ticket eligibility cycle (12 or 24 months)
    ticket_ratio = models.FloatField(db_column="fTktRatio", default=1.0)
    encash_ticket = models.BooleanField(db_column="bEncash", null=True)
    gl_code = models.IntegerField(db_column="nTktGLCode", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T06TKR10"
        verbose_name = "a7.Air Ticket Rule"

    def __str__(self):
        return f"{self.department}"
