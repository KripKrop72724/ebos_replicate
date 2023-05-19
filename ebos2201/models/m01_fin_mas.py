from django.db import models
from django.db.models import Max
from django.forms import ValidationError
from mptt.models import MPTTModel, TreeForeignKey

from ebos2201.models.m01_core_mas import T01Cur10, T01Div10, T01Nat10


# parent cannot be changed and level is the default field of the MPTT package
class T01Coa10(MPTTModel):
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column="IDCoaDiv")
    parent = TreeForeignKey(
        "self",
        models.PROTECT,
        db_column="IDParentAcct",
        limit_choices_to={"coa_control": "1"},
        blank=True,
        null=True,
    )
    account_name = models.CharField(db_column="sAcctName", max_length=50)
    ACCTYPE_CHOICE = (
        ("1", "GL"),
        ("2", "Bank"),
        ("3", "Cash"),
        ("4", "Card"),
        ("5", "COGS"),
        ("6", "Equity"),
    )
    account_type = models.CharField(
        db_column="sAccType", max_length=1, choices=ACCTYPE_CHOICE, default="1"
    )
    ACCGRP_CHOICE = (
        ("1", "Asset"),
        ("2", "Liability"),
        ("3", "Income"),
        ("4", "Expense"),
    )
    account_group = models.CharField(
        db_column="sAccGroup",
        max_length=1,
        choices=ACCGRP_CHOICE,
        default="1",
        blank=True,
    )
    COACTL_CHOICE = (("1", "Rollup"), ("2", "Postable"))
    coa_control = models.CharField(
        db_column="sCoAControl", max_length=1, choices=COACTL_CHOICE, default="2"
    )
    account_num = models.CharField(
        db_column="sAcctNum",
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Existing A/C number",
    )
    COASLCAT_CHOICE = (
        ("1", "Receivable"),
        ("2", "Payable"),
        ("3", "Fixed Asset"),
        ("4", "Entity"),
    )
    coa_sl_cat = models.CharField(
        db_column="IdCoaSlCat",
        max_length=1,
        choices=COASLCAT_CHOICE,
        blank=True,
        null=True,
    )
    coa_sl_type = models.ForeignKey(
        "T01Slt10", models.PROTECT, db_column="IdCoaSlType", blank=True, null=True
    )
    activity_group = models.ForeignKey(
        "T01Act10", models.PROTECT, db_column="IDCoaAct10", blank=True, null=True
    )
    cashflow_group = models.ForeignKey(
        "T01Cfl10", models.PROTECT, db_column="IDCoa_Cfl", blank=True, null=True
    )

    class MPTTMeta:
        order_insertion_by = ["account_name"]

    class Meta:
        db_table = "T01COA10"
        verbose_name = "b1.Chart of Account"

    def __str__(self):
        if self.account_num:
            return f"{self.account_num} - {self.account_name}"
        return f"{self.account_name}"

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)

        if (
            self.division
            and self.account_num
            and self.__class__.objects.filter(
                division=self.division, account_num=self.account_num
            )
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError(
                message=f"This existing A/C number for the `{self.division}` is duplicate",
                code="unique_together",
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.account_num:
            T01Coa10.objects.filter(id=self.id).update(account_num=self.id)


class T01Prj10(models.Model):
    project_code = models.CharField(db_column="sPrjCode", max_length=10, blank=True)
    project_name = models.CharField(db_column="sPrjName", max_length=150, blank=True)
    project_number = models.BigIntegerField(db_column="nPrjNo", null=True)
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDPrjDiv", null=True
    )
    project_subLedger = models.ForeignKey(
        "T01Sld10", models.PROTECT, db_column="IDPrjSL", null=True
    )
    project_address = models.CharField(db_column="sPrjAddr1", max_length=50, blank=True)
    estimated_value = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fEstValue", blank=True, null=True
    )
    actual_value = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fActValue", blank=True, null=True
    )
    project_status = models.SmallIntegerField(db_column="nPrjSts", null=True)
    project_COA = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IDPrjCOA",
        null=True,
        limit_choices_to={"coa_control": "2"},
    )
    project_WH = models.BigIntegerField(db_column="IDPrjWH", blank=True, null=True)

    class Meta:
        db_table = "T01PRJ10"
        verbose_name = "a5.Project Master"

    def __str__(self):
        return f"{self.division} - {self.project_number}"


class T01Sld10(models.Model):
    division = models.ForeignKey(
        "T01Div10", models.PROTECT, db_column="IdSldDiv", null=True
    )
    proxy_code = models.CharField(
        max_length=10,
        db_column="sProCode",
        choices=(("mas", "Master"), ("cus", "Customer"), ("sup", "Supplier")),
        default="mas",
    )
    subledger_name = models.CharField(db_column="sSLName", max_length=50)
    subledger_no = models.BigIntegerField(
        db_column="nSLNum", default=1000, editable=False
    )
    subledger_code = models.CharField(
        db_column="sSLCode", max_length=10, blank=True, verbose_name="Existing SL code"
    )
    subledger_type = models.ForeignKey(
        "T01Slt10", models.PROTECT, db_column="IDSLDType", blank=True, null=True
    )  # CU, EM
    SLCAT_CHOICE = (
        ("1", "Receivable"),
        ("2", "Payable"),
        ("3", "Fixed Asset"),
        ("4", "Entity"),
    )
    subledger_cat = models.CharField(
        db_column="IdSLDCat", max_length=1, choices=SLCAT_CHOICE, null=True
    )
    invoice_address1 = models.CharField(
        db_column="minvaddr1", max_length=50, blank=True
    )
    invoice_address2 = models.CharField(
        db_column="minvaddr2", max_length=50, blank=True
    )
    invoice_address3 = models.CharField(
        db_column="minvaddr3", max_length=50, blank=True
    )
    ship_to_address1 = models.CharField(
        db_column="sShipaddr1", max_length=50, blank=True
    )
    ship_to_address2 = models.CharField(
        db_column="sShipaddr2", max_length=50, blank=True
    )
    ship_to_address3 = models.CharField(
        db_column="sShipaddr3", max_length=50, blank=True
    )
    telephone1 = models.CharField(db_column="sPhone1", max_length=20, blank=True)
    telephone2 = models.CharField(db_column="sPhone2", max_length=20, blank=True)
    fax = models.CharField(db_column="sFax", max_length=20, blank=True)
    primary_contact_name = models.CharField(
        db_column="sPrimContact", max_length=50, blank=True
    )
    primary_email = models.EmailField(db_column="sEmail", blank=True, null=True)
    primary_mobile = models.CharField(db_column="sMobile", max_length=20, blank=True)
    commission_percent = models.FloatField(
        db_column="fCommPercent", blank=True, null=True
    )
    credit_days = models.IntegerField(db_column="nCrDays", blank=True, null=True)
    credit_days_from = models.ForeignKey(
        "T01Cdf10", models.PROTECT, db_column="sCrDaysFrom", blank=True, null=True
    )
    mode_of_payment = models.ForeignKey(
        "T01Mop10", models.PROTECT, db_column="IDMop10", blank=True, null=True
    )
    credit_limit = models.FloatField(db_column="fCrLimit", blank=True, null=True)
    credit_open = models.FloatField(db_column="fCrOpen", blank=True, null=True)
    due_amount = models.FloatField(db_column="fDueAmt", blank=True, null=True)
    as_of_date = models.DateField(db_column="dDueAsOf", blank=True, null=True)
    key_account_flag = models.BooleanField(
        db_column="bKeyAcct", default=False, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T01SLD10"
        verbose_name = "SubLedger Master Base"
        ordering = ("subledger_name",)

    def __str__(self) -> str:
        if self.subledger_code:
            return f"{self.subledger_code} - {self.subledger_name}"
        return self.subledger_name

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if (
            self.division
            and self.subledger_code
            and self.__class__.objects.exclude(id=self.id)
            .filter(
                division=self.division, subledger_code__icontains=self.subledger_code
            )
            .exists()
        ):
            raise ValidationError(
                message=f"This division and existing sl code already exists.",
                code="unique_together",
            )

    def save(self, *args, **kwargs):
        # Subleder number starting from 1000 and auto increment by 1
        if self._state.adding is True:
            try:
                sub_number = (
                    T01Sld10.objects.filter(division=self.division)
                    .only("subledger_no")
                    .aggregate(Max("subledger_no"))["subledger_no__max"]
                )
                if sub_number >= 1000:
                    self.subledger_no = sub_number + 1
            except Exception as e:
                pass

        if not self.subledger_code:
            self.subledger_code = self.subledger_no

        return super().save(*args, **kwargs)


# T01Sld10 proxy for subledger master
class T01SldM10Manager(models.Manager):
    def get_queryset(self):
        return super(T01SldM10Manager, self).get_queryset().filter(proxy_code="mas")


class T01SldM10(T01Sld10):
    objects = T01SldM10Manager()

    class Meta:
        proxy = True
        verbose_name = "b2.SubLedger Master"

    def save(self, *args, **kwargs):
        self.proxy_code = "mas"
        super(T01SldM10, self).save(*args, **kwargs)


class T01Slt10(models.Model):
    sl_type_desc = models.CharField(db_column="sSLTName", max_length=50)
    sl_type_code = models.CharField(db_column="sSLTCode", max_length=2, blank=True)
    division = models.ForeignKey(
        "T01Div10", models.PROTECT, db_column="IdSltDiv", null=True
    )

    class Meta:
        #    managed = False
        db_table = "T01SLT10"
        verbose_name = "b3.SubLedger Type"
        ordering = ("sl_type_desc",)

    def __str__(self):
        if self.sl_type_code:
            return f"{self.sl_type_code} - {self.sl_type_desc}"
        return self.sl_type_desc


class T01Bnk10(models.Model):
    division = models.ForeignKey(
        "T01Div10", models.PROTECT, db_column="IdDivBank", null=True
    )
    bank_name = models.CharField(db_column="sBnkName", max_length=50)
    bank_branch = models.CharField(db_column="sBranch", max_length=50, blank=True)
    bank_address = models.CharField(db_column="sAddress", max_length=50, blank=True)
    bank_city = models.CharField(db_column="sCity", max_length=50, blank=True)
    bank_postal_code = models.CharField(db_column="sPin", max_length=50, blank=True)
    bank_swift_code = models.CharField(
        db_column="sSWIFTcode", max_length=20, blank=True
    )
    bank_account = models.CharField(db_column="sACCTno", max_length=50, blank=True)
    bank_iban = models.CharField(db_column="sIBAN", max_length=50, blank=True)
    bank_tel = models.CharField(db_column="sTel", max_length=25, blank=True)
    bank_fax = models.CharField(db_column="sFax", max_length=25, blank=True)
    bank_email = models.CharField(db_column="sEmail", max_length=50, blank=True)
    bank_contact = models.CharField(db_column="sContname", max_length=50, blank=True)
    bank_mobile = models.CharField(db_column="sContMobile", max_length=30, blank=True)
    wps_routing_code = models.CharField(
        db_column="sWpsRoutingBnk", max_length=25, blank=True
    )
    wps_agent_code = models.CharField(
        db_column="sWpsAgentCode", max_length=15, blank=True
    )

    class Meta:
        db_table = "T01BNK10"
        verbose_name = "b4.Company Bank Account"

    def __str__(self):
        return self.bank_name


class T01Glc10(models.Model):
    gl_code = models.CharField(db_column="sGLCode", max_length=5, null=True)
    description = models.CharField(db_column="sGLDesc", max_length=30, blank=True)
    gl_category = models.CharField(
        db_column="sGlcodeCat", max_length=8, null=True
    )  # TableName / MenuID / App name /...

    class Meta:
        #    managed = False
        db_table = "T01GLC10"
        verbose_name = "c3.GL Code"

    def __str__(self) -> str:
        return self.gl_code


# credit days from (e.g: invoice, do, so ..etc) to normalize data during input
class T01Cdf10(models.Model):
    credit_days_from = models.CharField(
        db_column="sCrDaysFrom", max_length=25
    )  # Invoice, DO, SO ..etc
    document_type = models.CharField(
        db_column="sCrDaysDocType", max_length=10, blank=True
    )

    class Meta:
        #    managed = False
        db_table = "T01CDF10"
        verbose_name = "d4.Credit Days From"
        verbose_name_plural = "d4.Credit Days From"

    def __str__(self):
        return self.credit_days_from


# mode of payment, it was T01mode.IDmodepay, being used in esAccounts, esFP, esWO only.
class T01Mop10(models.Model):
    mode_of_pay = models.CharField(db_column="spaymode", max_length=10)
    mop_code = models.CharField(db_column="sMopCode", max_length=10, blank=True)

    class Meta:
        db_table = "T01MOP10"
        verbose_name = "d5.Mode of Pay"
        verbose_name_plural = "d5.Mode of Pay"

    def __str__(self) -> str:
        return self.mode_of_pay


class T01Cfl10(MPTTModel):
    parent = TreeForeignKey(
        "self", models.PROTECT, db_column="IDParentCfl", blank=True, null=True
    )
    cashflow_desc = models.CharField(
        db_column="sDesc",
        max_length=100,
    )
    cashflow_cat = models.IntegerField(db_column="nType", blank=True, null=True)
    CFLCTL_CHOICE = (("1", "Rollup"), ("2", "Postable"))
    Cfl_control = models.CharField(
        db_column="sCflControl", max_length=1, choices=CFLCTL_CHOICE, default="2"
    )
    division = models.ForeignKey(
        "T01Div10", models.PROTECT, db_column="IDCflDiv", null=True
    )

    class Meta:
        #    managed = False
        db_table = "T01CFL10"
        verbose_name = "c4.Cashflow Setup"

    class MPTTMeta:
        order_insertion_by = ["cashflow_desc"]

    def __str__(self):
        return self.cashflow_desc


class T01Act10(MPTTModel):
    parent = TreeForeignKey(
        "self", models.PROTECT, db_column="IDParentAct", blank=True, null=True
    )
    activity_name = models.CharField(db_column="sActName", max_length=50)
    activity_cat = models.IntegerField(db_column="nType", blank=True, null=True)
    ACTCTL_CHOICE = (("1", "Rollup"), ("2", "Postable"))
    Act_control = models.CharField(
        db_column="sActControl", max_length=1, choices=ACTCTL_CHOICE, default="2"
    )
    division = models.ForeignKey(
        "T01Div10",
        db_column="idActDiv",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        #    managed = False
        db_table = "T01ACT10"
        verbose_name = "c5.Activity Setup"

    class MPTTMeta:
        order_insertion_by = ["activity_name"]

    def __str__(self):
        return self.activity_name


# Payment gateway
class T01Stp10(models.Model):
    payment_id = models.CharField(
        max_length=150, db_column="sPayId", blank=True, null=True
    )
    email = models.EmailField(db_column="ePayEmail", blank=True, null=True)
    payment_method_types = models.CharField(
        max_length=15, db_column="sPayMethod", blank=True, null=True
    )
    description = models.CharField(
        max_length=150, db_column="sPaydes", blank=True, null=True
    )
    src_model = models.CharField(max_length=50, db_column="sPaySrcModel")
    src_model_id = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="dPayAmt", blank=True, null=True
    )
    currency = models.ForeignKey(T01Cur10, models.PROTECT, db_column="IdPayCurr")
    payment_status = models.CharField(
        max_length=15, db_column="sPayStatus", blank=True, null=True
    )
    payment_link = models.URLField(db_column="uPayLink", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expired_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "T01STP10"
        verbose_name = "c6.Stripe Payment"


# Sales Person
class T01Slm10(models.Model):
    first_name = models.CharField(db_column="sFrstNm", max_length=255)
    last_name = models.CharField(
        db_column="sLstNm", max_length=255, blank=True, null=True
    )
    mobile = models.CharField(db_column="sMobile", max_length=30, blank=True, null=True)
    telephone = models.CharField(
        db_column="stelephn", max_length=30, blank=True, null=True
    )
    email = models.EmailField(db_column="eEmail", max_length=255)
    commission_percent = models.DecimalField(
        max_digits=6, decimal_places=2, db_column="fCommPer", default=0.00
    )
    GENDER_CHOICE = (("male", "Male"), ("female", "Female"))
    gender = models.CharField(db_column="sGender", max_length=25, choices=GENDER_CHOICE)
    nationality = models.ForeignKey(
        T01Nat10, models.PROTECT, db_column="snatnality", max_length=40
    )
    subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdSld", blank=True, null=True
    )

    class Meta:
        db_table = "T01SLM10"
        verbose_name = "a6.Sales Person"

    def __str__(self):
        return f"{self.first_name} - {self.last_name }"


# Language
class T01Lan10(models.Model):
    language_name = models.CharField(db_column="sLanguage", max_length=40)

    class Meta:
        db_table = "T01LAN10"
        verbose_name = "a9.Language"

    def __str__(self) -> str:
        return self.language_name


# Sales Person Skill
class T01Slm11(models.Model):
    sales_person = models.ForeignKey(
        T01Slm10, models.PROTECT, db_column="IdSlm", null=True
    )
    language = models.ForeignKey(
        T01Lan10, models.PROTECT, db_column="IdLan", null=True, blank=True
    )
    read = models.BooleanField(db_column="bRead", default=False)
    write = models.BooleanField(db_column="bWrite", default=False)
    speak = models.BooleanField(db_column="bSpeak", default=False)

    class Meta:
        db_table = "T01SLM11"
        verbose_name = "Sales Person Skill"
