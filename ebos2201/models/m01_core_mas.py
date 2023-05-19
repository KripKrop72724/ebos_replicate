from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Max
from mptt.models import MPTTModel, TreeForeignKey

class CustomPermissionModel(models.Model):
    """
    This is a dummy model used to hold custom permissions.
    It should not hold any data.
    """
    
    class Meta:
        managed = False  # No database table creation or deletion operations will be performed for this model.
        permissions = [
            ('create_jv', 'Can create general voucher'),
            ('read_jv', 'Can read general voucher'),
            ('update_jv', 'Can update general voucher'),
            ('delete_jv', 'Can delete general voucher'),
            ('print_jv', 'Can print general voucher'),
            ('post_jv', 'Can post general voucher'),
            ('unpost_jv', 'Can unpost general voucher'),

            ('create_pv', 'Can create payment voucher'),
            ('read_pv', 'Can read payment voucher'),
            ('update_pv', 'Can update payment voucher'),
            ('delete_pv', 'Can delete payment voucher'),
            ('print_pv', 'Can print payment voucher'),
            ('post_pv', 'Can post payment voucher'),
            ('unpost_pv', 'Can unpost payment voucher'),

            ('create_rv', 'Can create receipt voucher'),
            ('read_rv', 'Can read receipt voucher'),
            ('update_rv', 'Can update receipt voucher'),
            ('delete_rv', 'Can delete receipt voucher'),
            ('print_rv', 'Can print receipt voucher'),
            ('post_rv', 'Can post receipt voucher'),
            ('unpost_rv', 'Can unpost receipt voucher'),

            ('create_dn', 'Can create debit note'),
            ('read_dn', 'Can read debit note'),
            ('update_dn', 'Can update debit note'),
            ('delete_dn', 'Can delete debit note'),
            ('print_dn', 'Can print debit note'),
            ('post_dn', 'Can post debit note'),
            ('unpost_dn', 'Can unpost debit note'),

            ('create_cn', 'Can create credit note'),
            ('read_cn', 'Can read credit note'),
            ('update_cn', 'Can update credit note'),
            ('delete_cn', 'Can delete credit note'),
            ('print_cn', 'Can print credit note'),
            ('post_cn', 'Can post credit note'),
            ('unpost_cn', 'Can unpost credit note'),
            
            ('create_subledger', 'Can create subledger'),
            ('read_subledger', 'Can read subledger'),
            ('update_subledger', 'Can update subledger'),
            ('delete_subledger', 'Can delete subledger'),

            ('create_coa', 'Can create coa'),
            ('read_coa', 'Can read coa'),
            ('update_coa', 'Can update coa'),
            ('delete_coa', 'Can delete coa'),

            ('create_allocation', 'Can create allocation'),
            ('read_allocation', 'Can read allocation'),
            ('update_allocation', 'Can update allocation'),
            ('delete_allocation', 'Can delete allocation'), 
            ('print_allocation', 'Can print allocation'),

            ('create_reports', 'Can create reports'),
            ('read_reports', 'Can read reports'),
            ('update_reports', 'Can update reports'),
            ('delete_reports', 'Can delete reports'),
            ('print_reports', 'Can print reports'),

            ('create_fs', 'Can create financial statement'),
            ('read_fs', 'Can read financial statement'),
            ('update_fs', 'Can update financial statement'),
            ('delete_fs', 'Can delete financial statement'),
            ('print_fs', 'Can delete financial statement'),

            ('read_dashboard', 'Can read dashboard'),
        ]



# Extended User Class
class User(AbstractUser):
    email = models.EmailField(unique=True)
    otp = models.CharField(db_column="cotp", max_length=6, blank=True, null=True)
    phone_number = models.CharField(
        db_column="cphone", max_length=12, unique=True, null=True
    )
    otp_expire_at = models.DateTimeField(db_column="dexpire", blank=True, null=True)
    class Meta(AbstractUser.Meta):
        ordering = ("username",)


class T01Cfg10(models.Model):
    license_name = models.CharField(
        db_column="sLicName", max_length=30, default="Demo Company"
    )
    software_name = models.CharField(
        db_column="sSoftwareName", max_length=10, default="ebos22"
    )
    num_of_users = models.IntegerField(db_column="nLicUsers", blank=True, null=True)
    date_issued = models.DateField(db_column="dLicIssued", null=True)
    date_expiry = models.DateField(db_column="dLicExpiry", null=True)
    robo_nick_name = models.CharField(
        db_column="sRoboName", max_length=10, default="ebos"
    )
    email_sender = models.EmailField(db_column="eEmail", max_length=100, null=True)
    password_sender = models.CharField(db_column="cpassword", max_length=100, null=True)
    display_print_in_new_tab = models.BooleanField(
        db_column="bDisplayPrtTab", default=True
    )

    class Meta:
        db_table = "T01CFG10"
        verbose_name = "e1.Configuration"

    def __str__(self):
        return self.license_name


class T01Cat10(models.Model):  # Category used in all modules
    category_code = models.IntegerField(db_column="nGrpNo", null=True)
    category_name = models.CharField(db_column="sGrpName", max_length=20, blank=True)
    system_code = models.CharField(
        db_column="sSysNo", max_length=2, blank=True, null=True
    )
    program_code = models.CharField(
        db_column="sPrgCode", max_length=8, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T01CAT10"
        ordering = ["category_code"]
        verbose_name = "a8.Category Master"

    def __str__(self):
        return f"{self.category_code}"


# parent cannot be changed and level is the default field of the MPTT package
class T01Com10(MPTTModel):
    parent = TreeForeignKey(
        "self", models.PROTECT, db_column="IDParentCo", blank=True, null=True
    )
    FYBEGIN_CHOICE = (
        (1, "Jan"),
        (2, "Feb"),
        (3, "Mar"),
        (4, "Apr"),
        (5, "May"),
        (6, "Jun"),
        (7, "Jul"),
        (8, "Aug"),
        (9, "Sep"),
        (10, "Oct"),
        (11, "Nov"),
        (12, "Dec"),
    )
    finyear_begin = models.IntegerField(
        db_column="nFYbegin", choices=FYBEGIN_CHOICE, null=True
    )
    company_name = models.CharField(db_column="sCompName", max_length=60)
    company_address = models.CharField(db_column="sCompAddr", max_length=60, blank=True)
    company_location = models.CharField(
        db_column="sCompLocation", max_length=60, blank=True
    )
    logo_file_link = models.FileField(
        upload_to="images/logos/", null=True, blank=True, default=None
    )
    document_header = models.CharField(
        db_column="sCompHeader", max_length=50, blank=True
    )
    document_footer = models.CharField(
        db_column="sCompFooter", max_length=50, blank=True
    )
    cost_type_co = models.IntegerField(
        db_column="nBuCstType", blank=True, null=True
    )  # average, fifo, fefo
    cost_level_co = models.IntegerField(
        db_column="nBuCstLevel", blank=True, null=True
    )  # cost by comp, div, wh
    active_status = models.BooleanField(db_column="bCompStatus", default=True)

    class Meta:
        db_table = "T01COM10"
        verbose_name = "a1.Company Master"

    class MPTTMeta:
        order_insertion_by = ["company_name"]

    def __str__(self):
        return self.company_name


class T01Div10(models.Model):
    company = models.ForeignKey(
        T01Com10, models.PROTECT, db_column="IDComDiv", null=True
    )
    division_name = models.CharField(db_column="sBuName", max_length=60)
    division_addr = models.CharField(db_column="BuAddress", max_length=60, blank=True)
    division_location = models.CharField(
        db_column="BuLocation", max_length=50, blank=True
    )
    currency = models.ForeignKey(
        "T01Cur10", models.PROTECT, db_column="IDDivCurr", null=True
    )
    wps_mol_uid = models.CharField(
        db_column="sMolRegEmpr", max_length=50, blank=True
    )  # Ministry of Labour ref
    wps_bank_code = models.ForeignKey(
        "T01Bnk10",
        on_delete=models.SET_NULL,
        db_column="IDPrlBnk",
        null=True,
        blank=True,
        related_name="payroll_bank_acc",
    )
    cost_type_div = models.IntegerField(
        db_column="nBuCstType", blank=True, null=True
    )  # average, fifo, fefo
    cost_level_div = models.IntegerField(
        db_column="nBuCstLevel", blank=True, null=True
    )  # cost by comp, div, wh
    checklist_popup = models.BooleanField(
        db_column="bChecklist", default=False
    )  # checklist before saving
    convert_to_caps = models.IntegerField(
        db_column="nCap", blank=True, null=True
    )  # 1 Caps, 2 Small, 0 doNothing
    invoice_ref_flag = models.BooleanField(db_column="bBuInvRef", null=True)
    sellprice_flag = models.BooleanField(
        db_column="bBuSellPrice", blank=True, null=True
    )
    user = models.ManyToManyField(
        User, db_column="IDUsers", blank=True, related_name="users"
    )
    permission_data = models.JSONField(blank=True, null=True)

    class Meta:
        #   managed = False  # reqd for existing DB with data, DB creation/modification/deletion handled manually
        db_table = "T01DIV10"
        verbose_name = "a2.Division"
        ordering = ("id",)

    def __str__(self):
        return self.division_name

    def get_div_comp(self):
        return self.company


class T01Dep10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDDivDep", null=True
    )
    department_code = models.CharField(db_column="sDepCode", max_length=5, blank=True)
    department_name = models.CharField(db_column="sDepName", max_length=50, blank=True)

    class Meta:
        db_table = "T01DEP10"
        verbose_name = "a3.Department"
        ordering = (
            "department_name",
            "division",
        )
        unique_together = ("department_name", "division")

    def __str__(self):
        return f"{self.division} - {self.department_name}"


class T01Dsg10(models.Model):
    department = models.ForeignKey(
        T01Dep10, models.PROTECT, db_column="IDDsgDep", null=True
    )
    designation = models.CharField(db_column="sDesName", max_length=50, blank=True)
    trade_category = models.CharField(db_column="sTrdCat", max_length=50, blank=True)
    payroll_group = models.ForeignKey(
        T01Cat10,
        models.PROTECT,
        db_column="sPayGroup",
        blank=True,
        null=True,
        limit_choices_to={"program_code": "T06Prs10"},
    )
    ATT_CHOICE = (
        ("A", "Automatic ATT booking"),
        ("M", "Manual ATT entry"),
        ("T", "TAM data import"),
    )
    attendance_type = models.CharField(
        db_column="sAttType", max_length=1, choices=ATT_CHOICE, default="A"
    )
    WEEKEND_CHOICE = (
        ("1", "Sat & Sun (day6+0)"),
        ("2", "Sunday (day0)"),
        ("3", "Fri & Sat (day5+6)"),
        ("4", "Friday (day5)"),
    )
    weekend_days = models.CharField(
        db_column="sWkendType", max_length=1, choices=WEEKEND_CHOICE, default="3"
    )  # sun=0 to sat=6
    average_daily_cost = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fCostPerDay", blank=True, null=True
    )
    hours_for_OT = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fHrs4OT", blank=True, null=True
    )  # book OT after hrs4ot worked
    ot_multiplier = models.FloatField(db_column="fOtMulti", default=1)  # ex: 0.5, 2.0

    class Meta:
        db_table = "T01DSG10"
        verbose_name = "a3.Designation"
        ordering = ("department__department_name", "designation")
        unique_together = ("department", "designation")

    def __str__(self):
        return f"{self.department} - {self.designation}"


class T01Whm10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDDivWh", null=True
    )
    warehouse_code = models.CharField(db_column="sWhCode", max_length=5, blank=True)
    warehouse_name = models.CharField(db_column="sWhName", max_length=50)
    batch_flag = models.BooleanField(db_column="bWhBatch", null=True)
    goods_return_recost = models.IntegerField(
        db_column="nBatReCalc", null=True
    )  # formulae 1,2,3 ..etc
    additional_cost_to_inventory = models.BooleanField(
        db_column="bWhInvAddCst", null=True
    )
    post_inventory_to_acct = models.BooleanField(db_column="bInvToAcc", null=True)
    cost_type_wh = models.IntegerField(
        db_column="nWhCstType", null=True
    )  # average, fifo, fefo
    cost_level_wh = models.IntegerField(
        db_column="nWhCstLevel", null=True
    )  # cost by branch, wh, comp

    class Meta:
        db_table = "T01WHM10"
        verbose_name = "a4.Warehouse Master"

    def __str__(self) -> str:
        return self.warehouse_name


# previously in Accounts Module as T10Job10


# Automated mail. email To/cc/bcc is from contact or subledger master based on certain logic
class T01Atm10(models.Model):
    email_code = models.CharField(
        db_column="semailCode", max_length=10, blank=True, null=True
    )
    report_name = models.CharField(
        db_column="srptname", max_length=40, blank=True, null=True
    )
    mail_from = models.EmailField(db_column="semailFrom", null=True)
    mail_to = models.EmailField(db_column="semailTo", null=True)
    subject = models.CharField(
        db_column="sSubject", max_length=100, blank=True, null=True
    )
    message = models.TextField(db_column="sMessage", blank=True, null=True)

    class Meta:
        #    managed = False # reqd for existing DB with data, DB creation/modification/deletion handled manually
        db_table = "T01ATM10"
        verbose_name = "e2.Setup Auto email"
        ordering = ["email_code"]

    def __str__(self) -> str:
        return f"{self.subject} - {self.email_code}"

    def auto_email(email_code, email_attachment):
        from ebos2201.notification import send_email

        get_T01Atm10 = T01Atm10.objects.filter(email_code=email_code.email_code).first()
        mail_from = get_T01Atm10.mail_from
        subject = get_T01Atm10.subject
        message = get_T01Atm10.message
        recipient_list = [
            get_T01Atm10.mail_to,
        ]
        attachement = None
        if email_attachment:
            attachement = email_attachment.path
        send_email(subject, message, recipient_list, mail_from, attachement)
        return True


class T01Cur10(models.Model):
    currency_name = models.CharField(db_column="sCurrName", max_length=50, blank=True)
    currency_code = models.CharField(db_column="sCurrCode", max_length=3)
    currency_symbol = models.CharField(
        db_column="sCurrSymbol", max_length=1, blank=True
    )

    class Meta:
        #    managed = False
        db_table = "T01CUR10"
        verbose_name = "b5.Currency Master"

    def __str__(self):
        return self.currency_code


class T01Cur11(models.Model):
    convert_curr_from = models.ForeignKey(
        T01Cur10,
        models.PROTECT,
        db_column="IDConvCurrFrom",
        related_name="convcurrfrom",
        null=True,
    )
    convert_curr_to = models.ForeignKey(
        T01Cur10,
        models.PROTECT,
        db_column="IDConvCurrTo",
        related_name="convcurrto",
        null=True,
    )
    buy_rate_ap = models.DecimalField(
        max_digits=10, decimal_places=4, db_column="fBuyRateAP", null=True
    )
    sell_rate_ar = models.DecimalField(
        max_digits=10, decimal_places=4, db_column="fSellRateAR", null=True
    )
    std_rate_gl = models.DecimalField(
        max_digits=10, decimal_places=4, db_column="fStdRateGL", null=True
    )
    date_effective_from = models.DateField(db_column="dEffFrom", null=True)

    class Meta:
        #    managed = False
        db_table = "T01CUR11"
        verbose_name = "b6.Currency Rate"

    def __str__(self) -> str:
        return f"{self.convert_curr_from} to {self.convert_curr_to}"

    def get_curr_rate(conv_curr_from, conv_curr_to, rate_as_of, module=""):
        try:
            obj = (
                T01Cur11.objects.annotate(max_date=Max("date_effective_from"))
                .filter(date_effective_from=F("max_date"))
                .get(
                    convert_curr_from=conv_curr_from,
                    convert_curr_to=conv_curr_to,
                    date_effective_from__lte=rate_as_of,
                )
            )

            if module == "ap":
                curr_rate = obj.buy_rate_app
            elif module == "ar":
                curr_rate = obj.sell_rate_ar
            else:
                curr_rate = obj.std_rate_gl

            return curr_rate
        except:
            raise ValueError("Not found the currency rate")


class T01Nat10(models.Model):  # nationality, used in esAccounts, esEM, esFP, esIS, esPR
    nationality = models.CharField(db_column="sNatEng", max_length=50)

    class Meta:
        db_table = "T01NAT10"
        ordering = ["nationality"]
        verbose_name = "a7.Nationality Master"

    def __str__(self) -> str:
        return self.nationality


class T01Slu10(models.Model):  # salutation, used in es32v5, esAccounts, esFP only
    salutation = models.CharField(db_column="sSalutation", max_length=10)

    class Meta:
        db_table = "T01SLU10"
        verbose_name = "d6.Salutation"

    def __str__(self) -> str:
        return self.salutation


class T01Uom10(models.Model):  # Used in esIN, esPR, esWO, eTender only
    unit_of_measure = models.CharField(db_column="sUomName", max_length=5)
    MEASURE_CHOICE = (
        ("1", "Count"),
        ("2", "Area"),
        ("3", "Volume"),
        ("4", "Weight"),
        ("5", "Time"),
    )
    measure_type = models.CharField(
        db_column="sUomType", max_length=1, choices=MEASURE_CHOICE, default="1"
    )
    unit_desc = models.CharField(db_column="sDesc", max_length=25, blank=True)

    class Meta:
        db_table = "T01UOM10"
        verbose_name = "d1.UoM Master"

    def __str__(self) -> str:
        return self.unit_of_measure


class T01Uom11(models.Model):  # used in esIN, esWO, eTender only
    unit_from = models.ForeignKey(
        T01Uom10,
        models.PROTECT,
        db_column="IDUOMfrom",
        related_name="UomFrom",
        null=True,
    )
    unit_to = models.ForeignKey(
        T01Uom10, models.PROTECT, db_column="IDUOMto", related_name="UomTo", null=True
    )
    conversion_rate = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fUomConv", null=True
    )

    class Meta:
        db_table = "T01UOM11"
        verbose_name = "d2.UoM Conversion"

    def __str__(self) -> str:
        return f"{self.unit_from} - {self.unit_to}"


# class T01Uom20(models.Model):
#     measure_type = models.IntegerField(db_column='nType', null=True)
#     # Area, Volume, Weight, Time ..etc
#     measure_name = models.CharField(db_column='sName', max_length=50, blank=True)

#     class Meta:
#         #    managed = False
#         db_table = 'T01UOM20'
#         verbose_name = 'd3.Unit Classification'

#     def __str__(self) -> str:
#         return f"{self.measure_type} {self.measure_name}"


class T01Voc10(models.Model):  # used in all modules
    proxy_code = models.CharField(
        max_length=3,
        db_column="sProxyCd",
        choices=(("voc", "voc"), ("doc", "doc")),
        default="voc",
    )
    division = models.ForeignKey(
        T01Div10, db_column="IdVocDiv", on_delete=models.CASCADE, null=True
    )
    prg_type = models.CharField(db_column="sPrgType", max_length=10, blank=True)
    system_num = models.CharField(
        max_length=2, db_column="sSysNum", blank=True, null=True
    )
    voucher_name = models.CharField(db_column="sName", max_length=40, blank=True)
    COASLCAT_CHOICE = (
        ("1", "Receivable"),
        ("2", "Payable"),
        ("3", "Fixed Asset"),
        ("4", "Entity"),
    )
    subledger_cat = models.CharField(
        db_column="sVocSLCat",
        max_length=1,
        choices=COASLCAT_CHOICE,
        null=True,
        blank=True,
    )
    subledger_type = models.ForeignKey(
        "T01Slt10",
        on_delete=models.SET_NULL,
        db_column="sVocSLType",
        null=True,
        blank=True,
    )
    # voucher to create DB / CR entries
    inv_trn_toacc = models.BooleanField(db_column="bInvToAcc", blank=True, null=True)
    # vocuher for 3 way match PO > REC > INV
    match_with_gr = models.BooleanField(db_column="bWithGR", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T01VOC10"
        verbose_name = "Voucher Control Base"

    def __str__(self) -> str:
        return self.voucher_name


class T01Voc11(models.Model):  # used in all modules
    voucher_name = models.ForeignKey(
        T01Voc10,
        on_delete=models.CASCADE,
        db_column="IDVoc10",
        blank=True,
        null=True,
        related_name="voc10",
    )
    voucher_type = models.CharField(db_column="sVocType", max_length=5)
    RESET_CHOICE = (
        ("C", "Continuous Number"),
        ("Y", "Yearly Reset"),
        ("M", "Monthly Reset"),
    )
    reset_type = models.CharField(
        db_column="sVocReset", max_length=1, choices=RESET_CHOICE, default="Y"
    )
    VCAT_CHOICE = (
        ("1", "Manual Entry"),
        ("2", "Automated Entry"),
        ("3", "Year closing"),
        ("4", "Audit Entry"),
    )
    voucher_cat = models.CharField(
        db_column="sVocCat", max_length=1, choices=VCAT_CHOICE, default="1"
    )
    POST_CHOICE = (("1", "Manual Post"), ("2", "Auto Post on Save"))
    post_option = models.CharField(
        db_column="sPostOpt", max_length=1, choices=POST_CHOICE, default="1"
    )
    UNPOST_CHOICE = (("reverse", "Reverse"), ("delete_record", "Delete record"))
    unpost_option = models.CharField(
        db_column="sUnpostOpt",
        max_length=15,
        choices=UNPOST_CHOICE,
        blank=True,
        null=True,
    )  # reverse, delete
    DELETE_CHOICE = (("1", "Mark as deleted"), ("2", "Delete from DB"))
    delete_option = models.CharField(
        db_column="sDelOpt", max_length=1, choices=DELETE_CHOICE, null=True, blank=True
    )
    print_header = models.BooleanField(db_column="bPrintOpt", default=True, null=True)
    save_and_print = models.BooleanField(
        db_column="bSaveNprint", default=False, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T01VOC11"
        verbose_name = "Voucher Type"
        ordering = ["voucher_type"]

    def __str__(self) -> str:
        if self.voucher_name.voucher_name:
            return f"{self.voucher_name.voucher_name} - {self.voucher_type}"
        return self.voucher_type

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if (
            self.voucher_name.division
            and self.voucher_type
            and self.__class__.objects.exclude(id=self.id)
            .filter(
                voucher_name__division=self.voucher_name.division,
                voucher_type=self.voucher_type,
            )
            .exists()
        ):
            raise ValidationError(
                message=f"Voucher Type with this ({self.voucher_name.division}, {self.voucher_type}) already exists.",
                code="unique_together",
            )


class T01Voc12(models.Model):  # used in all modules
    voucher_type = models.ForeignKey(
        T01Voc11, on_delete=models.CASCADE, db_column="IdVocType", blank=True, null=True
    )
    year_num = models.IntegerField(
        db_column="nYear", null=True, default=datetime.now().year
    )
    voucher_prefix = models.CharField(
        db_column="sVocPrefix", max_length=3, blank=True, default=""
    )
    voucher_suffix = models.CharField(
        db_column="sVocSuffix", max_length=3, blank=True, default=""
    )
    starting_num = models.BigIntegerField(
        db_column="nStartNum", null=True, default=1000
    )
    ending_num = models.BigIntegerField(db_column="nEndNum", null=True, default=9999)
    next_num = models.BigIntegerField(db_column="nNextNum", null=True, default=0)
    period_num = models.IntegerField(db_column="nPeriod", default=1, null=True)
    lock_flag = models.BooleanField(
        db_column="bVoc_Active", default=False, null=True, blank=True
    )
    pre_audit_close = models.BooleanField(
        db_column="bPreAuditclose", default=False, null=True, blank=True
    )
    audit_close = models.BooleanField(
        db_column="bAuditClose", default=False, null=True, blank=True
    )

    class Meta:
        db_table = "T01VOC12"
        verbose_name = "Voucher Setup Base"

    def __str__(self) -> str:
        return f"{self.voucher_type.voucher_type} - {self.year_num}"

    def clean(self) -> None:
        if T01Voc12.objects.filter(
            year_num=self.year_num, voucher_type=self.voucher_type
        ).exists():
            raise ValidationError("Already exist with this voucher type and year.")
        return super().clean()

    def open_period(ins):
        ins_obj = {
            "voucher_type": ins.voucher_type,
            "year_num": ins.year_num,
            "voucher_prefix": ins.voucher_prefix,
            "voucher_suffix": ins.voucher_suffix,
            "starting_num": ins.starting_num,
            "ending_num": ins.ending_num,
        }
        objs = [T01Voc12(period_num=i, **ins_obj) for i in reversed(range(2, 13))]
        T01Voc12.objects.bulk_create(objs)

        return True

    def next_number(vou_type, voc_date):
        """
        Discussion: 08-March-2023
        Pre audit close    audit close    voucher_cat
            False              False        1, 2  allow
            True               False        3,4  allow
            False              True              Error ("Pre audit skipped, audit closed, no entries allowed.")
            True               True              Error ("Audit closed, no entries allowed.")

        """
        year = voc_date.year
        period = voc_date.month

        voucher_objs = T01Voc12.objects.filter(
            voucher_type=vou_type, year_num=year, period_num=period
        )
        if voucher_objs.count() > 1:
            raise Exception("Duplicate setup for this voucher type.")
        elif voucher_objs.count() > 0:
            voucher_obj = voucher_objs[0]
            if voucher_obj.lock_flag:
                raise ValueError("Voucher locked.")
            elif (
                not voucher_obj.pre_audit_close
                and not voucher_obj.audit_close
                and voucher_obj.voucher_type.voucher_cat not in ["1", "2"]
            ):
                raise ValueError("No entries allowed.")
            elif (
                voucher_obj.pre_audit_close
                and not voucher_obj.audit_close
                and voucher_obj.voucher_type.voucher_cat not in ["3", "4"]
            ):
                raise ValueError("Year closed, please enter audit adjustment entries.")
            elif (
                not voucher_obj.pre_audit_close
                and voucher_obj.audit_close
            ):
                raise ValueError("Pre audit skipped, audit closed, no entries allowed.")
            elif (
                voucher_obj.pre_audit_close
                and voucher_obj.audit_close
            ):
                raise ValueError("Audit closed, no entries allowed.")
            else:
                if voucher_obj.next_num == 0:
                    next_num = voucher_obj.starting_num
                elif voucher_obj.voucher_type.reset_type == "C":
                    max_next_num = T01Voc12.objects.filter(
                        voucher_type=vou_type
                    ).aggregate(Max("next_num"))["next_num__max"]
                    next_num = max_next_num + 1
                elif voucher_obj.voucher_type.reset_type == "Y":
                    max_next_num = T01Voc12.objects.filter(
                        voucher_type=vou_type, year_num=year
                    ).aggregate(Max("next_num"))["next_num__max"]
                    next_num = max_next_num + 1
                elif voucher_obj.voucher_type.reset_type == "M":
                    next_num = voucher_obj.next_num + 1

                voucher_obj.next_num = next_num
                voucher_obj.save()

                return (
                    next_num,
                    f"{voucher_obj.voucher_prefix}{next_num}{voucher_obj.voucher_suffix}",
                )
        else:
            raise ValueError("Period not opened for voucher entry")


# Voucher control and Voucher setup proxy of T01Voc10, T01Voc12
class T01VocC10Manager(models.Manager):
    def get_queryset(self):
        return super(T01VocC10Manager, self).get_queryset().filter(proxy_code="voc")


class T01VocC10(T01Voc10):
    objects = T01VocC10Manager()

    class Meta:
        proxy = True
        verbose_name = "c1.Voucher Control"

    def save(self, *args, **kwargs):
        self.proxy_code = "voc"
        super(T01VocC10, self).save(*args, **kwargs)


class T01VocC12Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T01VocC12Manager, self)
            .get_queryset()
            .filter(voucher_type__voucher_name__proxy_code="voc")
        )


class T01VocC12(T01Voc12):
    objects = T01VocC12Manager()

    class Meta:
        proxy = True
        verbose_name = "c2.Voucher Setup"
