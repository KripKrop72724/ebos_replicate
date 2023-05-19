import codecs
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, Sum
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils.timezone import now

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2210.validator import validate_file_extension

from .m10_fin_link import T10Abs10, T10Gld10, T10Gld11, T10Pst10, T10Pst11, T10Sbs10


class T10Cfg10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDCfgDiv", null=True
    )
    internal_comment = models.IntegerField(db_column="nIntlComm", blank=True, null=True)
    inv_recd_date_edit = models.BooleanField(
        db_column="bInvRecdDate", blank=True, null=True
    )
    tolerance_perc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fTolerancePer",
        blank=True,
        null=True,
    )
    auto_supp_price = models.BooleanField(
        db_column="bAutoSupPrice", blank=True, null=True
    )
    auto_cost_price = models.BooleanField(
        db_column="bAutoCstPrice", blank=True, null=True
    )
    maximum_discount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="nMaximumDisc", blank=True, null=True
    )
    minimum_discount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="nMinimumMarg", blank=True, null=True
    )
    use_fifo_cost = models.BooleanField(db_column="bUseFIFOcost", blank=True, null=True)
    use_lifo_cost = models.BooleanField(db_column="bUseLIFOcost", blank=True, null=True)
    use_fefo_cost = models.BooleanField(db_column="bUseFEFOcost", blank=True, null=True)
    lock_date_change = models.BooleanField(
        db_column="bLockDtChange", blank=True, null=True
    )
    print_rollup_tot = models.BooleanField(
        db_column="bPrntRollTot", blank=True, null=True, default=False
    )

    class Meta:
        #    managed = False
        db_table = "T10CFG10"
        verbose_name = "a4.Finance Admin"

    def __str__(self) -> str:
        return f"{self.division} - {self.internal_comment}"


# GL voucher proxy model
class T10Jvm10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Jvm10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="JVM")
        )


class T10Jvm10(T10Gld10):
    objects = T10Jvm10Manager()

    class Meta:
        proxy = True
        verbose_name = "b1.GL Voucher"


# Unposted GL review
class T10Unp10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Unp10Manager, self)
            .get_queryset()
            .filter(Q(delete_flag=True) | Q(post_flag=False))
        )


class T10Unp10(T10Gld10):
    objects = T10Unp10Manager()

    class Meta:
        proxy = True
        verbose_name = "c3.Unposted GL review"


class T10Alc10(models.Model):
    is_cleaned = False

    division = models.ForeignKey(
        T01Div10, on_delete=models.CASCADE, db_column="IdAlcDiv", null=True
    )
    vou_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="sDocType", max_length=2, null=True
    )
    vou_num = models.BigIntegerField(db_column="nDocNo", blank=True, null=True)
    vou_date = models.DateField(db_column="dDoc", default=date.today)
    coa = models.ForeignKey(
        T01Coa10, models.PROTECT, db_column="IdAllcCoa", blank=True, null=True
    )
    subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdAllcSL", blank=True, null=True
    )
    DT_CHOICE = (("1", "Voucher Date"), ("2", "Due Date"))
    date_choice = models.CharField(
        db_column="sDt_choice", max_length=1, choices=DT_CHOICE, default="1"
    )
    date_from = models.DateField(
        db_column="dDateFrom", null=True, blank=True, verbose_name="db_date_from"
    )
    date_to = models.DateField(
        db_column="dDateTo", null=True, blank=True, verbose_name="db_date_to"
    )
    cr_date_from = models.DateField(db_column="dDateFromCr", blank=True, null=True)
    cr_date_upto = models.DateField(db_column="dDateUptoCr", blank=True, null=True)
    alloc_lock_flag = models.BooleanField(db_column="bAllocLock", blank=True, null=True)
    currency = models.ForeignKey(
        T01Cur10, models.PROTECT, db_column="sAlcCurr", blank=True, null=True
    )  # auto from T01Div10
    hdr_comment = models.CharField(
        db_column="sGLDcomment", max_length=80, blank=True, null=True
    )
    issued_to = models.CharField(
        db_column="sIssuedTo", max_length=40, blank=True, null=True
    )
    tot_amount = models.DecimalField(
        db_column="fAmount",
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=Decimal("0.00"),
    )
    line_narration = models.CharField(
        db_column="sNarration", max_length=80, blank=True, null=True
    )
    chq_num = models.CharField(db_column="sChqNo", max_length=25, blank=True, null=True)
    chq_date = models.DateField(db_column="dChqDt", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T10ALC10"
        verbose_name = "Allocation Header"
        ordering = ["vou_num"]

    def __str__(self) -> str:
        return f"{self.vou_num} {self.subledger}"

    def create_alloc_vou_num(vou_type, vou_date):
        try:
            next_num, next_num_pfx_sfx = T01Voc12.next_number(vou_type, vou_date)
            return next_num
        except Exception as e:
            raise ValidationError(e)

    # Getting data from T10Gld111 and import data to detail tables(T10Alc11,T10Alc12)
    def create_alloc_details(self):
        T10Alc11_items, T10Alc12_items = [], []
        debit_allocation_gl_records, credit_allocation_gl_records = None, None
        debit, credit = False, False

        try:
            # Filter GL Record on the basis of input fields - division and vou_date
            gld_data = T10Gld11.objects.filter(
                vou_id__division=self.division,
                vou_coa=self.coa,
                vou_subledger=self.subledger,
                vou_id__delete_flag=False,
                vou_id__post_flag=True,
            )

            if self.date_choice and self.date_choice == "2":  # Due Date = 1
                if self.date_from and self.date_to:
                    debit = True
                    debit_allocation_gl_records = gld_data.filter(
                        due_date__gte=self.date_from,
                        due_date__lte=self.date_to,
                        bcurr_debit__gt=Decimal("0.00"),
                    )

                if self.cr_date_from and self.cr_date_upto:
                    credit = True
                    credit_allocation_gl_records = gld_data.filter(
                        due_date__gte=self.cr_date_from,
                        due_date__lte=self.cr_date_upto,
                        bcurr_credit__gt=Decimal("0.00"),
                    )

            else:  # Voucher Date = 1
                if self.date_from and self.date_to:
                    debit = True
                    debit_allocation_gl_records = gld_data.filter(
                        vou_id__vou_date__gte=self.date_from,
                        vou_id__vou_date__lte=self.date_to,
                        bcurr_debit__gt=Decimal("0.00"),
                    )

                if self.cr_date_from and self.cr_date_upto:
                    credit = True
                    credit_allocation_gl_records = gld_data.filter(
                        vou_id__vou_date__gte=self.cr_date_from,
                        vou_id__vou_date__lte=self.cr_date_upto,
                        bcurr_credit__gt=Decimal("0.00"),
                    )

            # filtered data for Debit allocation (date_from, date_to)
            if debit_allocation_gl_records:
                for debit_record in debit_allocation_gl_records:
                    # Debit Details for inline
                    alloc_amt_tot = debit_record.alloc_amt_tot or 0
                    debit_open = debit_record.bcurr_debit + alloc_amt_tot

                    if debit_open > 0:
                        debit_ref = (
                            debit_record.vou_id.vou_hdr_ref
                            if debit_record.vou_id.vou_hdr_ref
                            else debit_record.vou_line_ref
                        )
                        debit_narration = (
                            debit_record.narration
                            if debit_record.narration
                            else f"{debit_record.vou_id.comment1 or ''} {debit_record.vou_id.comment2 or ''}"
                        )

                        # Create object for T10Alc11
                        T10Alc11_items.append(
                            {
                                "debit_id": debit_record.id,
                                "debit_alloc": debit_open,
                                "debit_ref": debit_ref,
                                "debit_vou": debit_record.vou_id.vou_num,
                                "debit_due_dt": debit_record.due_date,
                                "vou_date": debit_record.vou_id.vou_date,
                                "narration": debit_narration,
                                "debit_open": debit_open,
                            }
                        )
                        # End if

            # filtered data for credit allocation (cr_date_from, cr_date_upto)
            if credit_allocation_gl_records:
                for credit_record in credit_allocation_gl_records:
                    # Credit Details for inline
                    alloc_amt_tot = credit_record.alloc_amt_tot or 0
                    gl_credit_open = credit_record.bcurr_credit - alloc_amt_tot

                    if gl_credit_open > 0:
                        credit_ref = (
                            credit_record.vou_id.vou_hdr_ref
                            if credit_record.vou_id.vou_hdr_ref
                            else credit_record.vou_line_ref
                        )
                        credit_narration = (
                            credit_record.narration
                            if credit_record.narration
                            else f"{credit_record.vou_id.comment1 or ''} {credit_record.vou_id.comment2 or ''}"
                        )

                        # Create object for T10Alc12
                        T10Alc12_items.append(
                            {
                                "credit_id": credit_record.id,
                                "credit_alloc": gl_credit_open,
                                "credit_ref": credit_ref,
                                "credit_vou": credit_record.vou_id.vou_num,
                                "credit_due_dt": credit_record.due_date,
                                "vou_date": credit_record.vou_id.vou_date,
                                "narration": credit_narration,
                                "credit_open": gl_credit_open,
                            }
                        )

            if len(T10Alc11_items) < 0 and len(T10Alc12_items) < 0:
                raise ValidationError("No record found")

            return debit, credit, T10Alc11_items, T10Alc12_items

        except Exception as e:
            raise ValidationError("No record found")

    # Checking for debit=credit on edit
    # insert the total alloc into T10Gld11
    # alloc_lock_flag as True
    def update_alloc_details(self):
        try:
            for alc11 in self.allocation_db.all():
                if alc11.debit_alloc > 0:
                    gld11_obj = T10Gld11.objects.filter(id=alc11.debit_id)
                    total_alloc_amt_db = gld11_obj[0].alloc_amt_tot - alc11.debit_alloc
                    gld11_obj.update(alloc_amt_tot=total_alloc_amt_db)

            # T10Alc12
            for alc12 in self.allocation_cr.all():
                if alc12.credit_alloc > 0:
                    gld11_obj = T10Gld11.objects.filter(id=alc12.credit_id)
                    total_alloc_amt_cr = alc12.credit_alloc + gld11_obj[0].alloc_amt_tot
                    gld11_obj.update(alloc_amt_tot=total_alloc_amt_cr)
            T10Alc10.objects.filter(id=self.id).update(alloc_lock_flag=True)
        except Exception as e:
            raise ValidationError(e)

    # Call the function when deleting
    # If alloc_lock_flag is True, before deleting the alloc details, reverse the T10Gld11 alloc total
    # Otherwise delete
    def unpost_allocation(self):
        for alc11 in self.allocation_db.all():
            if alc11.debit_alloc > 0:
                gld11_obj = T10Gld11.objects.filter(id=alc11.debit_id)
                gld11_tot_alloc_amt_db = gld11_obj[0].alloc_amt_tot
                gld11_tot_alloc_amt_db += alc11.debit_alloc
                gld11_obj.update(alloc_amt_tot=gld11_tot_alloc_amt_db)

        # T10Alc12
        for alc12 in self.allocation_cr.all():
            if alc12.credit_alloc > 0:
                gld11_obj = T10Gld11.objects.filter(id=alc12.credit_id)
                gld11_tot_alloc_amt_cr = gld11_obj[0].alloc_amt_tot
                gld11_tot_alloc_amt_cr -= alc12.credit_alloc
                gld11_obj.update(alloc_amt_tot=gld11_tot_alloc_amt_cr)


# Model manager to use in Proxy model T10Gla10
class T10Gla10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Gla10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="GLA")
        )


# GL Allocation proxy model
class T10Gla10(T10Alc10):
    objects = T10Gla10Manager()

    class Meta:
        proxy = True
        verbose_name = "b3.GL Allocation"

    def clean(self):
        """check validation rules here"""
        try:
            if self.id is None:
                (
                    self.debit,
                    self.credit,
                    self.T10Alc11_items,
                    self.T10Alc12_items,
                ) = self.create_alloc_details()
                self.vou_num = T10Alc10.create_alloc_vou_num(
                    self.vou_type, self.vou_date
                )
                self.alloc_lock_flag = False
            else:
                self.update_alloc_details()
        except Exception as e:
            raise ValidationError(e)

        self.is_cleaned = True

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()
        if self._state.adding:
            super().save(*args, **kwargs)
            # Insert data into T10Alc11, T10ALc12
            T10Alc11.objects.bulk_create(
                [
                    T10Alc11(alloc_id_id=self.pk, **alc11)
                    for alc11 in self.T10Alc11_items
                ]
            )
            T10Alc12.objects.bulk_create(
                [
                    T10Alc12(alloc_id_id=self.pk, **alc12)
                    for alc12 in self.T10Alc12_items
                ]
            )


class T10Alc11(models.Model):
    alloc_id = models.ForeignKey(
        T10Alc10,
        on_delete=models.CASCADE,
        db_column="IdDbAlloc",
        null=True,
        blank=True,
        related_name="allocation_db",
    )
    debit_id = models.BigIntegerField(db_column="IdGldAlcDb", blank=True, null=True)
    debit_vou = models.BigIntegerField(db_column="nAllocDbVou", blank=True, null=True)
    debit_ref = models.CharField(
        db_column="sDbInvRef", max_length=10, blank=True, null=True
    )  # T10Gld10.inv_ref
    debit_open = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fGlOpenDebit", blank=True, null=True
    )
    debit_alloc = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fGlDebit", blank=True, null=True
    )
    debit_due_dt = models.DateField(db_column="dDateDueDr", blank=True, null=True)
    vou_date = models.DateField(db_column="dVocDate", default=date.today)
    narration = models.CharField(
        db_column="sAlcNarr", max_length=80, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T10ALC11"
        ordering = ["alloc_id"]
        verbose_name = "Allocation Dr Detail"


class T10Alc12(models.Model):
    alloc_id = models.ForeignKey(
        T10Alc10,
        on_delete=models.CASCADE,
        db_column="IdCrAlloc",
        null=True,
        blank=True,
        related_name="allocation_cr",
    )
    credit_id = models.BigIntegerField(db_column="IdGldAlcCr", blank=True, null=True)
    credit_vou = models.BigIntegerField(db_column="nAllocCrVou", blank=True, null=True)
    credit_ref = models.CharField(
        db_column="sCrInvRef", max_length=10, blank=True, null=True
    )
    credit_open = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fGlOpenCredit",
        blank=True,
        null=True,
    )
    credit_alloc = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fGlCredit", blank=True, null=True
    )
    credit_due_dt = models.DateField(db_column="dDateDueCr", blank=True, null=True)
    vou_date = models.DateField(db_column="dVocDate", default=date.today)
    narration = models.CharField(
        db_column="sAlcNarr", max_length=80, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T10ALC12"
        ordering = ["alloc_id"]
        verbose_name = "Allocation Cr Detail"


class T10Brc10(models.Model):
    proxy_code = models.CharField(
        max_length=6,
        db_column="sProCode",
        choices=(("manual", "Manual"), ("auto", "Automatic")),
        default="manual",
    )
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdBrcDiv", null=True
    )
    bank_account = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdBrcCoa",
        blank=True,
        null=True,
        limit_choices_to={"account_type": "2", "coa_control": "2"},
    )
    date_from = models.DateField(db_column="dDateFrom", blank=True, null=True)
    date_to = models.DateField(db_column="dDateTo", blank=True, null=True)
    opening_gl_bal = models.DecimalField(
        db_column="fOpGlBal", max_digits=10, decimal_places=2, blank=True, null=True
    )
    closing_gl_bal = models.DecimalField(
        db_column="fClGlBal", max_digits=10, decimal_places=2, blank=True, null=True
    )
    reco_gl_bal = models.DecimalField(
        db_column="fRecoGlBal", max_digits=10, decimal_places=2, blank=True, null=True
    )
    opening_stmt_bal = models.DecimalField(
        db_column="fOpStmtBal", max_digits=10, decimal_places=2, blank=True, null=True
    )
    closing_stmt_bal = models.DecimalField(
        db_column="fClStmtBal", max_digits=10, decimal_places=2, blank=True, null=True
    )
    import_bank_stmt = models.FileField(
        db_column="fImpBankStmt",
        upload_to="bank_statement/",
        blank=True,
        null=True,
        validators=[validate_file_extension],
    )

    class Meta:
        #    managed = False
        db_table = "T10BRC10"
        verbose_name = "Bank Reconciliation"

    def __str__(self) -> str:
        return f"{self.division} - {self.bank_account}"

    def create_gl_transaction_T10Brc11(self):
        # Filtering data from T10Gld11 on basis of COA and date range
        if t10gld10_records := T10Gld11.objects.filter(
            vou_coa=self.bank_account,
            vou_id__vou_date__gte=self.date_from,
            vou_id__vou_date__lte=self.date_to,
        ):

            gl_transaction_items, bank_stmt_items = [], None

            for record in t10gld10_records:
                gl_transaction_items.append(
                    {
                        "gl_id": record,
                        "gl_date": record.due_date,
                        "gl_debit": record.bcurr_debit,
                        "gl_credit": record.bcurr_credit,
                        "narration": record.narration,
                        "chq_num": record.chq_num,
                        "chq_date": record.chq_date,
                    }
                )
            if self.proxy_code == "auto":
                bank_stmt_items = self.create_bank_stmt_T10Brc12()
                return gl_transaction_items, bank_stmt_items
            return gl_transaction_items
        else:
            raise ValueError("No GLD record found")

    # Read bank statement csv file
    def create_bank_stmt_T10Brc12(self):
        auto_bank_reco = []
        auto_bank_reco = csv.reader(
            codecs.iterdecode(self.import_bank_stmt, "utf-8"), delimiter=","
        )
        for i, stmt in enumerate(auto_bank_reco):
            if i == 0:
                continue
            stm_date = datetime.strptime(stmt[0], "%Y/%m/%d").strftime("%Y-%m-%d")
            if stm_date >= self.date_from and stm_date <= self.date_to:
                auto_bank_reco.append(
                    {
                        "stmt_date": stm_date,
                        "narration": stmt[1],
                        "stmt_debit": Decimal(stmt[2] or 0.00),
                        "stmt_credit": Decimal(stmt[3] or 0.00),
                    }
                )

        return auto_bank_reco

    # function to update reco_gl_bal of T10Brc10
    def update_reco_gl_bal(id):
        # filtering record on the basis of status = "Reconciled"
        reco_objs = T10Brc11.objects.filter(bank_reco_id=id)
        gl_debit = 0
        gl_credit = 0

        reconciled_records = reco_objs.filter(status="1")
        if reconciled_records.exists():
            for reconciled_record in reconciled_records:
                gl_debit += reconciled_record.gl_debit
                gl_credit += reconciled_record.gl_credit

                # if status in brc11 is '1' means reconciled , then update corresponding record in gld11 record with brc11 id
                T10Gld11.objects.filter(id=reconciled_record.gl_id.id).update(
                    bank_reco_id=reconciled_record.id
                )

        non_reconciled_records = reco_objs.exclude(status="1")
        if non_reconciled_records.exists():
            for non_reconciled_record in non_reconciled_records:
                gl_debit += non_reconciled_record.gl_debit
                gl_credit += non_reconciled_record.gl_credit

                # if status in brc11 is not '1' remove bank_reco_id in gld11 record
                T10Gld11.objects.filter(id=non_reconciled_record.gl_id.id).update(
                    bank_reco_id=None
                )

        reco_gl_bal = gl_debit - gl_credit
        T10Brc10.objects.filter(id=id).update(reco_gl_bal=reco_gl_bal)

        return True

    def reconcile_bank_stmnt(obj):
        T10Brc10_id = obj.id

        # fetch record from T10Brc12 linked to T10Brc10
        get_T10Brc12_records = T10Brc12.objects.filter(bank_reco_id=T10Brc10_id)
        for record in get_T10Brc12_records:
            stmt_debit = record.stmt_debit
            stmt_credit = record.stmt_credit

            # fetch record from T10Brc11 those gl_date == stmt_date
            get_T10Brc11_records = T10Brc11.objects.filter(
                bank_reco_id=T10Brc10_id, gl_date=record.stmt_date
            )
            for T10Brc11_record in get_T10Brc11_records:
                gl_debit = T10Brc11_record.gl_debit
                gl_credit = T10Brc11_record.gl_credit
                if stmt_debit == gl_debit and stmt_credit == gl_credit:
                    T10Brc11_record.update(status="1")

        op_bal = T10Abs10.coa_opening_bal(
            obj.bank_account.id, obj.date_from, obj.division.id
        )
        # After adding 1 day in date_From
        date_to = obj.date_to
        cl_date = date_to + timedelta(days=1)
        cl_bal = T10Abs10.coa_opening_bal(obj.bank_account.id, cl_date, obj.division.id)

        # updating opening_gl_bal,closing_gl_bal field of T10Brc10
        T10Brc10.objects.filter(id=T10Brc10_id).update(
            opening_gl_bal=op_bal, closing_gl_bal=cl_bal
        )
        return True


class T10Brc11(models.Model):
    bank_reco_id = models.ForeignKey(
        T10Brc10, models.PROTECT, db_column="IdGlBrc", null=True
    )
    gl_id = models.ForeignKey(
        T10Gld11,
        models.PROTECT,
        db_column="IdGldVoc",
        null=True,
        verbose_name="Vou num",
    )
    gl_date = models.DateField(db_column="dGlDate", blank=True, null=True)
    gl_debit = models.DecimalField(
        db_column="fGlDebit",
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=Decimal("0.00"),
    )
    gl_credit = models.DecimalField(
        db_column="fGlCredit",
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=Decimal("0.00"),
    )
    narration = models.CharField(
        db_column="sNarration", max_length=80, blank=True, null=True
    )
    chq_num = models.CharField(db_column="sChqNo", max_length=25, blank=True, null=True)
    chq_date = models.DateField(db_column="dChqdt", blank=True, null=True)
    STATUS_CHOICES = (
        ("1", "Reconciled"),
        ("2", "Chq/DD issued not presented"),
        ("3", "Chq/DD deposited Not in Cr"),
        ("4", "Statement Amount Not in GL"),
        ("5", "GL amount Not in Statement"),
        ("6", "Others Net"),
    )
    status = models.CharField(
        db_column="sStatus", choices=STATUS_CHOICES, max_length=1, blank=True, null=True
    )
    comment = models.CharField(
        db_column="sCommentBrc", max_length=80, blank=True, null=True
    )

    class Meta:
        db_table = "T10BRC11"
        verbose_name = "Bank GL Transaction"

    def __str__(self) -> str:
        return f"{self.bank_reco_id} - {self.gl_id}"


# Perform action after save of T10Brc11
@receiver(models.signals.post_save, sender=T10Brc11)
def update_reco_gl_bal_T10Brc10(sender, instance, **kwargs):
    bank_reco_id = instance.bank_reco_id.id
    T10Brc10.update_reco_gl_bal(bank_reco_id)


class T10Brc12(models.Model):
    bank_reco_id = models.ForeignKey(
        T10Brc10, models.PROTECT, db_column="IdStmtBrc", null=True
    )
    stmt_date = models.DateField(db_column="dstmtDate", blank=True, null=True)
    stmt_debit = models.DecimalField(
        db_column="fstmtDebit",
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=Decimal("0.00"),
    )
    stmt_credit = models.DecimalField(
        db_column="fstmtCredit",
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=Decimal("0.00"),
    )
    narration = models.CharField(
        db_column="sNarration", max_length=80, blank=True, null=True
    )

    class Meta:
        db_table = "T10BRC12"
        verbose_name = "Bank Statement"

    def __str__(self) -> str:
        return f"{self.bank_reco_id} - {self.stmt_date}"


# Perform action after save of T10Brc12
@receiver(models.signals.post_save, sender=T10Brc12)
def update_opening_closing_gl_bal_T10Brc10(sender, instance, **kwargs):
    T10Brc10.reconcile_bank_stmnt(instance.bank_reco_id)


# Manual bank reconcillation proxy
class T10Mbr10Manager(models.Manager):
    def get_queryset(self):
        return super(T10Mbr10Manager, self).get_queryset().filter(proxy_code="manual")


class T10Mbr10(T10Brc10):
    objects = T10Mbr10Manager()

    class Meta:
        proxy = True
        verbose_name = "b4.Manual Bank Reconciliation"

    def clean(self):
        """check validation rules here"""
        try:
            if self.id is None:
                self.gl_transaction_items = self.create_gl_transaction_T10Brc11()
        except Exception as e:
            raise ValidationError(e)

        self.is_cleaned = True

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()

        self.proxy_code = "manual"
        if self._state.adding:
            super().save(*args, **kwargs)
            # Insert data into T10Brc11
            T10Brc11.objects.bulk_create(
                [
                    T10Brc11(bank_reco_id_id=self.pk, **brc11)
                    for brc11 in self.gl_transaction_items
                ]
            )


# Automatic bank reconcillation proxy
class T10Abr10Manager(models.Manager):
    def get_queryset(self):
        return super(T10Abr10Manager, self).get_queryset().filter(proxy_code="auto")


class T10Abr10(T10Brc10):
    is_cleaned = False
    objects = T10Abr10Manager()

    class Meta:
        proxy = True
        verbose_name = "b5.Auto Bank Reconciliation"

    def clean(self):
        """check validation rules here"""
        try:
            if self.id is None:
                (
                    self.gl_transaction_items,
                    self.bank_stmt_items,
                ) = self.create_gl_transaction_T10Brc11()
        except Exception as e:
            raise ValidationError(e)

        self.is_cleaned = True

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()

        self.proxy_code = "auto"
        if self._state.adding:
            super().save(*args, **kwargs)
            # Insert data into T10Brc11, T10Brc12
            T10Brc11.objects.bulk_create(
                [
                    T10Brc11(bank_reco_id_id=self.pk, **brc11)
                    for brc11 in self.gl_transaction_items
                ]
            )
            T10Brc12.objects.bulk_create(
                [
                    T10Brc12(bank_reco_id_id=self.pk, **brc12)
                    for brc12 in self.bank_stmt_items
                ]
            )


class T10Fyc10(models.Model):
    is_cleaned = False
    division = models.ForeignKey(
        T01Div10, on_delete=models.CASCADE, db_column="IdFycDiv", null=True
    )
    closing_year = models.IntegerField(db_column="nClsYear", blank=True, null=True)
    closing_opt = models.CharField(
        db_column="sClsOpt",
        max_length=15,
        choices=(
            ("pre_audit_close", "Pre audit close"),
            ("audit_close", "Audit close"),
        ),
    )
    net_profit_loss = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fPrfitLoss", blank=True, null=True
    )
    vou_date = models.DateField(db_column="dVouDate", blank=True, null=True)
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="sGlCode", null=True
    )
    vou_curr = models.ForeignKey(
        T01Cur10, models.PROTECT, db_column="IDFycCurr", blank=True, null=True
    )
    vou_hdr_ref = models.CharField(
        max_length=200, db_column="sVouHdrRef", blank=True, null=True
    )
    auto_entry_flag = models.BooleanField(db_column="bAutoEntry", blank=True, null=True)

    class Meta:
        db_table = "T10FYC10"
        verbose_name = "c4.Financial Year closing"

    def __str__(self) -> str:
        return f"{self.division} - {self.closing_year}"

    def year_closing(self):
        # For T10Sbs10 table
        # clbal = next year opening bal
        # clbal = openning + p12 + audit adjust
        sld_objs = T01Sld10.objects.all()
        for sld_obj in sld_objs:
            try:
                t10sbs10_obj = T10Sbs10.objects.get(
                    subledger_id=sld_obj, fin_year=self.closing_year
                )

                period_cum_bal = T10Sbs10.sl_period_cum_bal(t10sbs10_obj.__dict__, 12)

                # update closing balance
                # opening + pre_audit_clbal + sl_audit_adj
                sbs_clbal_net = Decimal(t10sbs10_obj.sl_opbal or 0) + period_cum_bal + Decimal(
                    t10sbs10_obj.sl_audit_adj or 0
                )
                t10sbs10_obj.sl_clbal = sbs_clbal_net
                t10sbs10_obj.save()

                sbs_obj = T10Sbs10.objects.filter(
                    fin_year=self.closing_year + 1, subledger_id=sld_obj
                )

                if sbs_obj.exists():
                    sbs_obj.update(sl_opbal=Decimal(t10sbs10_obj.sl_clbal or 0))
                else:
                    T10Sbs10.objects.create(
                        subledger_id=sld_obj, fin_year=self.closing_year + 1, sl_opbal=t10sbs10_obj.sl_clbal
                    )
            except ObjectDoesNotExist as e:
                pass

        income, expense = 0.00, 0.00
        coa_objs = T01Coa10.objects.all()

        for coa_obj in coa_objs:
            try:
                t10abs10_obj = T10Abs10.objects.get(
                    coa_id=coa_obj, fin_year=self.closing_year
                )

                pre_audit_clbal = T10Abs10.coa_period_cum_bal(t10abs10_obj.__dict__, 12)

                # update closing balance
                # opening + pre_audit_clbal + coa_audit_adj
                coa_clbal_net = Decimal(t10abs10_obj.coa_opbal or 0) + pre_audit_clbal + Decimal(
                    t10abs10_obj.coa_audit_adj or 0
                )
                t10abs10_obj.coa_clbal = coa_clbal_net
                t10abs10_obj.save()

                # Insert NEW record for next year
                if int(coa_obj.account_group) in [3, 4]:  # income=3, expense=4
                    opbal = 0
                    if int(coa_obj.account_group) == 3:
                        income = Decimal(income) + Decimal(coa_clbal_net)
                    else:
                        expense = Decimal(expense) + Decimal(coa_clbal_net)
                else:
                    opbal = Decimal(t10abs10_obj.coa_clbal or 0)

                abs_obj = T10Abs10.objects.filter(
                    fin_year=self.closing_year + 1, coa_id=coa_obj
                )

                if abs_obj.exists():
                    abs_obj.update(coa_opbal=opbal)
                    # update the unpost_option for physically delete voucher
                    t01voc11_obj = T01Voc11.objects.filter(voucher_cat=3)
                    t01voc11_obj.update(unpost_option="delete_record")

                    # Call auto_gl_unpost(), if same year closing voucher already exists
                    # T10Gld10.auto_gl_unpost(
                    #     T10Gld10.objects.get(
                    #         vou_type=t01voc11_obj[0],
                    #         vou_date=date(self.closing_year, 12, 31),
                    #     )
                    # )
                else:
                    T10Abs10.objects.create(
                        coa_id=coa_obj, fin_year=self.closing_year + 1, coa_opbal=opbal
                    )
            except ObjectDoesNotExist as e:
                pass
        
        # update pre_audit_close and audit_close in T10Voc12
        voc_obj = T01Voc12.objects.filter(year_num=self.closing_year)
        if self.closing_opt == "pre_audit_close":
            voc_obj.update(pre_audit_close=True, audit_close=False)
        if self.closing_opt == "audit_close":
            voc_obj.update(pre_audit_close=True, audit_close=True)

        return income, expense

    def net_profit_loss_bal(self):  
        try:
            income, expense = self.year_closing()
            # inc = -100, exp = +50, difference = inc + exp = -100 + 50 = -50(negative means profit)
            # income = 0, exp = 50, difference = 50 (positive menas loss)
            difference = Decimal(income or 0) + Decimal(expense or 0)
            self.net_profit_loss = (-1) * difference
            self.vou_curr = self.division.currency
            self.vou_date = date(self.closing_year, 12, 31)
        except Exception as e:
            raise ValueError(e)
        
    def clean(self):
        """check validation rules here"""
        try:
            self.net_profit_loss_bal()
            # Create YC voucher
            # mapping_data = {
            #     field.name: self.__getattribute__(field.name)
            #     for field in self._meta.fields
            # }
            # T10Gld10.auto_gl_post(self.gl_code.id, self.vou_curr, mapping_data)
            self.is_cleaned = True
        except Exception as e:
            raise ValidationError(e)

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()

        super().save(*args, **kwargs)


class T10BaseGlr01(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdGlrDiv", null=True
    )
    file_csv = models.FileField(
        upload_to="reports/",
        max_length=250,
        null=True,
        db_column="fGlrCsv",
        blank=True,
        default=None,
    )
    file_pdf = models.FileField(
        upload_to="reports/",
        max_length=250,
        null=True,
        db_column="fGlrPdf",
        blank=True,
        default=None,
    )

    class Meta:
        abstract = True


# Glr06/01 >>>>   GLC (contra a/c bal), GLR (running balance)
class T10Glr01(T10BaseGlr01):
    rpt_code = models.CharField(
        db_column="sRptCode", max_length=3, blank=True, null=True
    )
    coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdRbalCoa",
        blank=True,
        null=True,
        limit_choices_to={"coa_control": "2"},
    )
    subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdRbalSL", blank=True, null=True
    )
    vou_curr = models.ForeignKey(
        T01Cur10, models.PROTECT, db_column="IdRbalCUR", blank=True, null=True
    )
    aging1 = models.IntegerField(db_column="nAging1", blank=True, null=True, default=30)
    aging2 = models.IntegerField(db_column="nAging2", blank=True, null=True, default=60)
    aging3 = models.IntegerField(db_column="nAging3", blank=True, null=True, default=90)
    dt_from = models.DateField(db_column="dRbalFrom", null=True, default=now)
    dt_upto = models.DateField(db_column="dRbalUpto", null=True, default=now)

    class Meta:
        db_table = "T10GLR01"
        ordering = ["division"]
        verbose_name = "GLR Primary Model 01"


#  GL Running Balance Detail
class T10GlrB01Manager(models.Manager):
    def get_queryset(self):
        return super(T10GlrB01Manager, self).get_queryset().filter(rpt_code="GLR")


class T10GlrB01(T10Glr01):
    objects = T10GlrB01Manager()

    class Meta:
        proxy = True
        verbose_name = "d1.GL Stmt Running Balance"

    def save(self, *args, **kwargs):
        self.rpt_code = "GLR"
        super(T10GlrB01, self).save(*args, **kwargs)


#  GL Contra Balance Detail proxy model
class T10Glc01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Glc01Manager, self).get_queryset().filter(rpt_code="GLC")


class T10Glc01(T10Glr01):
    objects = T10Glc01Manager()

    class Meta:
        proxy = True
        verbose_name = "d2.GL Stmt Contra Balance"

    def save(self, *args, **kwargs):
        self.rpt_code = "GLC"
        super(T10Glc01, self).save(*args, **kwargs)


#  Statement of Accounts proxy model
class T10Stm01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Stm01Manager, self).get_queryset().filter(rpt_code="SAO")


class T10Stm01(T10Glr01):
    objects = T10Stm01Manager()

    class Meta:
        proxy = True
        verbose_name = "d3.Statement of Account Outstanding"

    def save(self, *args, **kwargs):
        self.rpt_code = "SAO"
        super(T10Stm01, self).save(*args, **kwargs)


#  Statement of Accounts proxy model
class T10Stm02Manager(models.Manager):
    def get_queryset(self):
        return super(T10Stm02Manager, self).get_queryset().filter(rpt_code="SAD")


class T10Stm02(T10Glr01):
    objects = T10Stm02Manager()

    class Meta:
        proxy = True
        verbose_name = "d4.Statement of Account Detail"

    def save(self, *args, **kwargs):
        self.rpt_code = "SAD"
        super(T10Stm02, self).save(*args, **kwargs)


#  Day Book Proxy Model
class T10Dbk01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Dbk01Manager, self).get_queryset().filter(rpt_code="DBK")


class T10Dbk01(T10Glr01):
    objects = T10Dbk01Manager()

    class Meta:
        proxy = True
        verbose_name = "d8.Day Book"

    def save(self, *args, **kwargs):
        self.rpt_code = "DBK"
        super(T10Dbk01, self).save(*args, **kwargs)


#  Subledger Summary By COA
class T10SlCoa01Manager(models.Manager):
    def get_queryset(self):
        return super(T10SlCoa01Manager, self).get_queryset().filter(rpt_code="SLC")


class T10SlCoa01(T10Glr01):
    # account = models.ForeignKey(T01Coa10, models.PROTECT, db_column='IdCoaRollUp', null=True , limit_choices_to={'coa_control':'1'} )
    objects = T10SlCoa01Manager()

    class Meta:
        proxy = True
        verbose_name = "d6.Subledger Balance asof Date"

    def save(self, *args, **kwargs):
        self.rpt_code = "SLC"
        super(T10SlCoa01, self).save(*args, **kwargs)


#  Subledger Summary By COA
class T10SlCoa02Manager(models.Manager):
    def get_queryset(self):
        return super(T10SlCoa02Manager, self).get_queryset().filter(rpt_code="SLD")


class T10SlCoa02(T10Glr01):
    objects = T10SlCoa02Manager()

    class Meta:
        proxy = True
        verbose_name = "d7.Subledger Balance btw Date"

    def save(self, *args, **kwargs):
        self.rpt_code = "SLD"
        super(T10SlCoa02, self).save(*args, **kwargs)


#  Ledger Account Summary
class T10LdgAcc01Manager(models.Manager):
    def get_queryset(self):
        return super(T10LdgAcc01Manager, self).get_queryset().filter(rpt_code="LEA")


class T10LdgAcc01(T10Glr01):
    objects = T10LdgAcc01Manager()

    class Meta:
        proxy = True
        verbose_name = "d5.Control A/C Balance by Subledger"

    def save(self, *args, **kwargs):
        self.rpt_code = "LEA"
        super(T10LdgAcc01, self).save(*args, **kwargs)


#  Chart Account Summary
class T10ChrAcc01Manager(models.Manager):
    def get_queryset(self):
        return super(T10ChrAcc01Manager, self).get_queryset().filter(rpt_code="CRA")


class T10ChrAcc01(T10Glr01):
    objects = T10ChrAcc01Manager()

    class Meta:
        proxy = True
        verbose_name = "d51.Control A/C Balance by COA"

    def save(self, *args, **kwargs):
        self.rpt_code = "CRA"
        super(T10ChrAcc01, self).save(*args, **kwargs)


#  Aging Report Summary
class T10AgRpt01Manager(models.Manager):
    def get_queryset(self):
        return super(T10AgRpt01Manager, self).get_queryset().filter(rpt_code="AGR")


class T10AgRpt01(T10Glr01):
    objects = T10AgRpt01Manager()

    class Meta:
        proxy = True
        verbose_name = "d9.Aging Report"

    def save(self, *args, **kwargs):
        self.rpt_code = "AGR"
        super(T10AgRpt01, self).save(*args, **kwargs)


# Glr02/03/04/05 >>>>   BS, TB, PL,  TBC
class T10Glr02(T10BaseGlr01):
    rpt_code = models.CharField(
        db_column="sRptCode", max_length=5, blank=True, null=True
    )
    company = models.ForeignKey(
        T01Com10, models.PROTECT, db_column="IdGlrCom", null=True
    )
    RPT_CHOICE = (("1", "Opening"), ("2", "Closing"), ("3", "Monthly"))
    type_of_rpt = models.CharField(
        db_column="sBStype", max_length=1, choices=RPT_CHOICE, default=1, null=True
    )
    year = models.IntegerField(db_column="nRptYear", null=True, blank=True)
    MONTH_CHOICE = (
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
        (13, "Q1"),
        (14, "Q2"),
        (15, "Q3"),
        (16, "Q4"),
        (17, "H1"),
        (18, "H2"),
    )
    month = models.IntegerField(
        db_column="nRptMonth",
        choices=MONTH_CHOICE,
        blank=True,
        null=True,
        verbose_name="Period",
    )
    day = models.IntegerField(db_column="nRptDate", blank=True, null=True)
    as_of_date = models.DateField(db_column="dtAsof", blank=True, null=True)
    without_zero_value = models.BooleanField(db_column="bZeroVal", default=False)

    class Meta:
        db_table = "T10GLR02"
        verbose_name = "GLR Primary Model 02"
        ordering = ("year",)

    def clean(self) -> None:
        if self.type_of_rpt == "3" and not self.month:
            raise ValidationError({"month": "Month is required."})
        return super().clean()


# Trial Balance Report
class T10Tb01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Tb01Manager, self).get_queryset().filter(rpt_code="TB")


class T10Tb01(T10Glr02):
    objects = T10Tb01Manager()

    class Meta:
        proxy = True
        verbose_name = "e2.Trial Balance"

    def save(self, *args, **kwargs):
        self.rpt_code = "TB"
        super(T10Tb01, self).save(*args, **kwargs)


# Balance Sheet Report
class T10Bs01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Bs01Manager, self).get_queryset().filter(rpt_code="BS")


class T10Bs01(T10Glr02):
    objects = T10Bs01Manager()

    class Meta:
        proxy = True
        verbose_name = "e3.Balance Sheet"

    def save(self, *args, **kwargs):
        self.rpt_code = "BS"
        super(T10Bs01, self).save(*args, **kwargs)


# Profit/Loss Report
class T10Pl01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Pl01Manager, self).get_queryset().filter(rpt_code="PL")


class T10Pl01(T10Glr02):
    objects = T10Pl01Manager()

    class Meta:
        proxy = True
        verbose_name = "e4.Profit or Loss Statement"

    def save(self, *args, **kwargs):
        self.rpt_code = "PL"
        super(T10Pl01, self).save(*args, **kwargs)


# Trial Balance Check List
class T10Tbc01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Tbc01Manager, self).get_queryset().filter(rpt_code="TBC")


class T10Tbc01(T10Glr02):
    objects = T10Tbc01Manager()

    class Meta:
        proxy = True
        verbose_name = "e1.Trial Balance Check List"

    def clean(self) -> None:
        if not self.month:
            raise ValidationError({"month": "Month is required."})

        return super().clean()

    def save(self, *args, **kwargs):
        self.rpt_code = "TBC"
        super(T10Tbc01, self).save(*args, **kwargs)


# Trial Balance Report -- Consolidated Trial Balance Sheet
class T10Ctb01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Ctb01Manager, self).get_queryset().filter(rpt_code="CTB")


class T10Ctb01(T10Glr02):
    objects = T10Ctb01Manager()

    class Meta:
        proxy = True
        verbose_name = "e5.Consolidated Trial Balance"

    def save(self, *args, **kwargs):
        self.rpt_code = "CTB"
        super(T10Ctb01, self).save(*args, **kwargs)


#  Cash Flow Statement
class T10CshFlow01Manager(models.Manager):
    def get_queryset(self):
        return super(T10CshFlow01Manager, self).get_queryset().filter(rpt_code="CSF")


class T10CshFlow01(T10Glr02):
    objects = T10CshFlow01Manager()

    class Meta:
        proxy = True
        verbose_name = "e6.Cash Flow Statement"

    def clean(self) -> None:
        if not self.month:
            raise ValidationError({"month": "Month is required."})

    def save(self, *args, **kwargs):
        self.rpt_code = "CSF"
        super(T10CshFlow01, self).save(*args, **kwargs)


# Trial Balance as of date
class T10TbDt01Manager(models.Manager):
    def get_queryset(self):
        return super(T10TbDt01Manager, self).get_queryset().filter(rpt_code="TBDT")


class T10TbDt01(T10Glr02):
    objects = T10TbDt01Manager()

    class Meta:
        proxy = True
        verbose_name = "e7.Trial Balance as of date"

    def clean(self) -> None:
        if not self.as_of_date:
            raise ValidationError({"as_of_date": "As of date is required."})

    def save(self, *args, **kwargs):
        self.rpt_code = "TBDT"
        super(T10TbDt01, self).save(*args, **kwargs)


# Balance sheet as of date
class T10BsDt01Manager(models.Manager):
    def get_queryset(self):
        return super(T10BsDt01Manager, self).get_queryset().filter(rpt_code="BSDT")


class T10BsDt01(T10Glr02):
    objects = T10BsDt01Manager()

    class Meta:
        proxy = True
        verbose_name = "e8.Balance Sheet as of date"

    def clean(self) -> None:
        if not self.as_of_date:
            raise ValidationError("As of date is required.")

    def save(self, *args, **kwargs):
        self.rpt_code = "BSDT"
        super(T10BsDt01, self).save(*args, **kwargs)


# Profit & Lose statement as of date
class T10PlDt01Manager(models.Manager):
    def get_queryset(self):
        return super(T10PlDt01Manager, self).get_queryset().filter(rpt_code="PLDT")


class T10PlDt01(T10Glr02):
    objects = T10PlDt01Manager()

    class Meta:
        proxy = True
        verbose_name = "e9.Profit & Lose Statement as of date"

    def clean(self) -> None:
        if not self.as_of_date:
            raise ValidationError("As of date is required.")

    def save(self, *args, **kwargs):
        self.rpt_code = "PLDT"
        super(T10PlDt01, self).save(*args, **kwargs)


class T10Tic10(models.Model):
    company = models.ForeignKey(
        T01Com10, models.PROTECT, db_column="IDComTic", null=True
    )
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDTicDiv", null=True
    )
    vou_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="IDTicVoc", null=True
    )
    from_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IDFromCoa",
        null=True,
        related_name="from_coa_set",
        limit_choices_to={"coa_control": "2"},
    )
    from_sl = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IDTicSld", null=True
    )
    ic_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IDIcCoa",
        null=True,
        related_name="ic_coa_set",
        limit_choices_to={"coa_control": "2"},
    )
    vou_dtfrom = models.DateField(null=True)
    vou_dtto = models.DateField(null=True)
    from_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fFromAmt", blank=True, null=True
    )
    flag_db_cr = models.CharField(
        db_column="sDbCrFlag",
        max_length=2,
        blank=True,
        choices=(("db", "DB"), ("cr", "CR")),
    )
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="sGLCode", null=True
    )
    aa_code = models.IntegerField(db_column="nAACode", null=True)

    class Meta:
        db_table = "T10TIC10"
        verbose_name = "b5.Inter Company Transaction"
        unique_together = ("gl_code", "aa_code")

    def __str__(self) -> str:
        return f"{self.gl_code}, {self.aa_code}"

    def save(self, *args, **kwargs):
        self.from_amt = T10Gld11.objects.filter(
            vou_id__post_flag=True,
            vou_id__division=self.division,
            vou_id__vou_type=self.vou_type,
            vou_coa=self.from_coa,
            vou_subledger=self.from_sl,
            vou_date__range=[self.vou_dtfrom, self.vou_dtto],
        ).aggregate(amt_diff=Sum("bcurr_debit") - Sum("bcurr_credit"))

        self.flag_db_cr = "db" if self.from_amt > 0 else "cr"
        super().save(*args, **kwargs)

    def __posting_setup_detail(self):
        try:
            narration = (
                "Post intercompany / division balance for {division} and {gl_code}"
            )
            # For T10Tic11, call auto_gl_post()
            for inter_com in self.inter_com_set.all():
                pst10_obj = T10Pst10.objects.create(
                    gl_code=inter_com.gl_code,
                    aa_code=inter_com.aa_code,
                    system_code="10",
                    description="Post intercompany / division balance",
                    vou_type=inter_com.vou_type,
                    division=inter_com.division,
                )
                T10Pst11.objects.bulk_create(
                    [
                        T10Pst11(
                            aa_code=pst10_obj.pk,
                            amount_field="to_amt",
                            coa_code=inter_com.to_coa,
                            flag_db_cr="db",
                            subledger_field="to_subledger",
                            voc_narration_dict=narration,
                        ),
                        T10Pst11(
                            aa_code=pst10_obj.pk,
                            amount_field="to_amt",
                            coa_code=inter_com.ic_coa,
                            flag_db_cr="cr",
                            voc_narration_dict=narration,
                        ),
                    ]
                )
                detali_line_obj = {
                    "division": inter_com.division,
                    "gl_code": inter_com.gl_code,
                    "vou_date": inter_com.alloc_date,
                    "to_amt": inter_com.to_amt,
                    "to_subledger": inter_com.to_subledger.id,
                }
                T10Gld10.auto_gl_post(
                    inter_com.gl_code.id, inter_com.division.currency, detali_line_obj
                )
                T10Pst10.objects.filter(id=pst10_obj.pk).delete()
        except Exception as ex:
            raise ValueError(f"An exception occur: {ex}")

    def __posting_setup(self):
        try:
            # For T10Tic10, call auto_gl_post()
            parent_obj = T10Pst10.objects.create(
                gl_code=self.gl_code,
                aa_code=self.aa_code,
                system_code="10",
                description="Post intercompany / division balance",
                vou_type=self.vou_type,
                division=self.division,
            )
            narration = (
                "Post intercompany / division balance for {division} and {gl_code}"
            )
            T10Pst11.objects.bulk_create(
                [
                    T10Pst11(
                        aa_code=parent_obj.pk,
                        amount_field="total_to_amt",
                        coa_code=self.from_coa,
                        flag_db_cr="cr",
                        subledger_field="from_sl",
                        voc_narration_dict=narration,
                    ),
                    T10Pst11(
                        aa_code=parent_obj.pk,
                        amount_field="total_to_amt",
                        coa_code=self.ic_coa,
                        flag_db_cr="db",
                        voc_narration_dict=narration,
                    ),
                ]
            )

            header_line_obj = {
                "division": self.division,
                "gl_code": self.gl_code,
                "vou_date": self.vou_dtto,
                "total_to_amt": self.inter_com_set.aggregate(Sum("to_amt")),
                "from_sl": self.from_sl.id,
            }
            T10Gld10.auto_gl_post(
                self.gl_code.id, self.division.currency, header_line_obj
            )
            T10Pst10.objects.filter(id=parent_obj.pk).delete()

            self.__posting_setup_detail()

            return 1
        except Exception as ex:
            raise ValueError(f"An exception occur: {ex}")

    def post_intercompany_balance(self):
        self.__posting_setup()


class T10Tic11(models.Model):
    inter_com = models.ForeignKey(
        T10Tic10,
        db_column="IDInterCom",
        on_delete=models.CASCADE,
        related_name="inter_com_set",
    )
    company = models.ForeignKey(
        T01Com10, models.PROTECT, db_column="IDComTic", null=True
    )
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDTicDiv", null=True
    )
    vou_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="IDTicVoc", null=True
    )
    to_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IDToCoa",
        null=True,
        related_name="to_coa_set",
        limit_choices_to={"coa_control": "2"},
    )
    to_subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IDTicSld", null=True
    )
    ic_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IDIcCoa",
        null=True,
        related_name="intercom_coa_set",
        limit_choices_to={"coa_control": "2"},
    )
    percent_alloc = models.FloatField(
        verbose_name="Percent allocation (%)", db_column="fPercAlloc"
    )
    to_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fToAmt", blank=True, null=True
    )
    alloc_date = models.DateField(null=True)
    narration = models.CharField(
        max_length=50, db_column="sNarration", blank=True, null=True
    )
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="sGLCode", null=True
    )
    aa_code = models.IntegerField(db_column="nAACode", null=True)

    class Meta:
        db_table = "T10TIC11"
        verbose_name = "Inter Company Trn Detail"

    def __str__(self) -> str:
        return f"{self.gl_code}, {self.aa_code}"

    def save(self, *args, **kwargs):
        self.to_amt = Decimal(self.inter_com.from_amt) * Decimal(
            self.percent_alloc / 100
        )
        self.alloc_date = self.inter_com.vou_dtto
        super().save(*args, **kwargs)
