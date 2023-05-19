from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django import forms
from django.db import models

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2210.models.m10_fin_link import T10Tib10

from .m10_fin_gl import T10Alc10, T10Alc11, T10Alc12, T10Gld10, T10Gld11

# Account payable


# Allocated payment vocuher
class T10Apv10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Apv10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="APV")
        )


class T10Apv10(T10Alc10):
    object = T10Apv10Manager()

    class Meta:
        proxy = True
        verbose_name = "p7.Allocate and Pay"
        verbose_name_plural = "p7.Allocate and Pay"

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


# Payment vouchers
# Bank payment voucher proxy model
class T10Bpv10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Bpv10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="BPV")
        )


class T10Bpv10(T10Gld10):
    objects = T10Bpv10Manager()

    class Meta:
        proxy = True
        verbose_name = "p4.Bank Payment Voucher"


# Cash payment voucher proxy model
class T10Cpv10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Cpv10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="CPV")
        )


class T10Cpv10(T10Gld10):
    objects = T10Cpv10Manager()

    class Meta:
        proxy = True
        verbose_name = "p5.Cash Payment Voucher"


class T10Crn10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Crn10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="CRN")
        )


class T10Crn10(T10Gld10):
    objects = T10Crn10Manager()

    class Meta:
        proxy = True
        verbose_name = "p3.Credit Note"


# Account Payable Invoice
class T10Api10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Api10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="API")
        )


class T10Api10(T10Gld10):
    objects = T10Api10Manager()

    class Meta:
        proxy = True
        verbose_name = "p1.Payable Invoice"


# Tax Invoice AP header proxy
class T10Tip10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Tip10Manager, self)
            .get_queryset()
            .filter(inv_type__voucher_name__prg_type="TIP")
        )


class T10Tip10(T10Tib10):
    objects = T10Tip10Manager()

    class Meta:
        proxy = True
        verbose_name = "p2.Tax Invoice Payable"


def next_chq_num(chq_book):
    used_chq_num = chq_book.begin_num + chq_book.used_num
    next_chq_num = chq_book.used_num + 1
    # T10Chq11.objects.update(id=chq_book.id,used_num=next_chq_num)
    return used_chq_num


# Perform action after save of proxy model T10Bpv10
# @receiver(post_save, sender=T10Gld11)
# def register_transaction(sender, instance, **kwargs):
#     bpv_header = T10Gld10.objects.get(id=instance.vou_id.id)
#     chq_amount = Decimal(instance.bcurr_debit or 0.00) + Decimal(instance.bcurr_credit or 0.00)
#     if  bpv_header.vou_type.voucher_name.prg_type =='BPV':
#         chq_layout , chq_book = None , None
#         chq_control = T10Chq10.objects.filter(bank_coa=instance.vou_coa)
#         if chq_control.count() > 0:
#             chq_layout = chq_control[0]
#         else:
#             chq_layout=T10Chq10.objects.create(bank_coa=instance.vou_coa,date_format=0, date_xpixel=420, date_ypixel=750, pay_to_xpixel=80, pay_to_ypixel=710, amt_num_xpixel=410, amt_num_ypixel=660, amt_txt1_xpixel=80, amt_txt1_ypixel=680, amt_txt2_xpixel=40,  amt_txt2_ypixel=655)
#         chq_books = T10Chq11.objects.filter(Chq_layout_id=chq_layout,Book_Status = 'new')
#         if chq_books.count() > 0:
#             chq_book = chq_books[0]
#         else:
#             chq_book=T10Chq11.objects.create(Chq_layout_id=chq_layout , chq_book_ref='' , begin_num = 1001 , end_num = 1010 , Book_Status = 'new')

#         chq_transaction = T10Chq20.objects.filter(bpv_id=bpv_header.id)
#         if chq_transaction.count()> 0:
#             trans_id = chq_transaction[0].id
#         else:
#             used_chq_num = next_chq_num(chq_book)
#             T10Chq20.objects.create(chq_layout_id=chq_layout, bpv_id=bpv_header.id , chq_book_id=chq_book , chq_num = used_chq_num ,
#                                     chq_amt=chq_amount , chq_status = 'issued' , status_note = '')


# PDC payments
class T10Ppd10(models.Model):
    PDC_CHOICES = (("ap", "ap"), ("ar", "ar"))
    pdc_code = models.CharField(
        max_length=2, db_column="sPDC", choices=PDC_CHOICES, null=True
    )
    division = models.ForeignKey(
        T01Div10, on_delete=models.CASCADE, db_column="IdPpdDiv", null=True
    )
    gl_date_from = models.DateField(db_column="dtGlFrm", null=True)
    gl_date_to = models.DateField(db_column="dtGlTo", null=True)
    pdc_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdPdcCoa",
        blank=True,
        null=True,
        related_name="pdc_coa_set",
        limit_choices_to={"account_type": "2", "coa_control": "2"},
    )
    bank_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdBnkCoa",
        blank=True,
        null=True,
        related_name="bank_coa_set",
        limit_choices_to={"account_type": "2", "coa_control": "2"},
    )
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="IdGLCode", null=True
    )

    class Meta:
        verbose_name = "PDC Header"

    def __str__(self):
        return f"{self.division} {self.gl_date_from}-{self.gl_date_to}"

    def import_PDC_data(self):
        t10gld11_objs = T10Gld11.objects.filter(
            chq_date__range=(self.gl_date_from, self.gl_date_to), vou_coa=self.pdc_coa
        )

        if self.pdc_code == "ap":
            t10gld11_objs = t10gld11_objs.filter(bcurr_credit__gt=0)
        else:
            t10gld11_objs = t10gld11_objs.filter(bcurr_debit__gt=0)

        for obj in t10gld11_objs:
            amount_field = (
                obj.bcurr_credit if self.pdc_code == "ap" else obj.bcurr_debit
            )
            T10Ppd11.objects.create(
                pdc_id=self,
                gl_id=obj,
                vou_type=obj.vou_id.vou_type,
                vou_date=obj.vou_id.vou_date,
                amount=amount_field,
                vou_curr=obj.base_curr,
                hdr_ref=obj.vou_id.vou_hdr_ref,
                comment=obj.vou_id.comment1,
                chq_num=obj.chq_num,
                chq_date=obj.chq_date,
                chq_status=obj.chq_status,
            )


class T10Ppd11(models.Model):
    pdc_id = models.ForeignKey(
        T10Ppd10,
        on_delete=models.CASCADE,
        db_column="IdPDC10",
        related_name="pdc_payment",
    )
    gl_id = models.ForeignKey(
        T10Gld11,
        models.PROTECT,
        db_column="nGlId",
        blank=True,
        null=True,
        related_name="gld11_set",
        verbose_name="Vou num",
    )
    vou_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="IdVouTyp", null=True
    )
    vou_date = models.DateField(db_column="dtVou", blank=True, null=True)
    amount = models.DecimalField(db_column="dAmt", max_digits=10, decimal_places=2)
    vou_curr = models.ForeignKey(
        T01Cur10, models.PROTECT, db_column="IdVouCurr", blank=True, null=True
    )
    hdr_ref = models.CharField(
        db_column="sHdrRef", max_length=10, blank=True, null=True
    )
    comment = models.CharField(
        db_column="scomment", max_length=80, blank=True, null=True
    )
    chq_num = models.CharField(db_column="sChqNo", max_length=25, blank=True, null=True)
    chq_date = models.DateField(db_column="dtChq", blank=True, null=True)
    CHQSTATUS_CHOICE = (
        ("1", "Issued"),
        ("2", "Deposited"),
        ("3", "On-Hold"),
        ("4", "Honored"),
        ("5", "Bounced"),
        ("6", "Withdrawn"),
    )
    chq_status = models.CharField(
        db_column="sChqStatus",
        max_length=1,
        choices=CHQSTATUS_CHOICE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "PDC Detail"

    def __str__(self):
        return f"{self.vou_type} - {self.vou_type}"

    @property
    def get_gl_id(self):
        return self.gl_id.vou_num

    def update_pdc_status(self):
        if int(self.chq_status) in [5, 6]:
            T10Gld10.gl_data_reverse(
                self.gl_id.vou_id.vou_num, self.vou_type, self.vou_date, self.chq_date
            )

    def save(self, *args, **kwargs):
        if self.pk:
            self.update_pdc_status()
        super().save(*args, **kwargs)


# PDC payment proxy
class T10PdcAp10Manager(models.Manager):
    def get_queryset(self):
        return super(T10PdcAp10Manager, self).get_queryset().filter(pdc_code="ap")


class T10PdcAp10(T10Ppd10):
    objects = T10PdcAp10Manager()

    class Meta:
        proxy = True
        verbose_name = "p6.PDC Payable Review"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.pdc_code = "ap"
            super(T10PdcAp10, self).save(*args, **kwargs)
            self.import_PDC_data()


# Model manager to use in Proxy model T10Pal10
class T10Pal10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Pal10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="PAL")
        )


# Payment allocation
class T10Pal10(T10Alc10):
    ap_allocation_prg = str
    object = T10Pal10Manager()

    class Meta:
        proxy = True
        verbose_name = "p8.Payment Allocation"


# Payables projection
# class T10Ppr10(models.Model):
#     class Meta:
#         verbose_name = "Payables Projection"


# Cheque Printing Module
class T10Chq10(models.Model):
    bank_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdBankCoa",
        null=True,
        limit_choices_to={"account_type": "2", "coa_control": "2"},
    )
    bank_name = models.CharField(
        db_column="sBankName", max_length=50, blank=True, null=True
    )
    chq_image = models.FileField(upload_to="images/logos/", null=True, blank=True)
    date_format = models.CharField(
        db_column="sDateFormat", max_length=11, blank=True, null=True
    )
    date_xpixel = models.IntegerField(
        db_column="nDtXpix", blank=True, null=True, default=420
    )
    date_ypixel = models.IntegerField(
        db_column="nDtYpix", blank=True, null=True, default=750
    )
    pay_to_xpixel = models.IntegerField(
        db_column="nPayToXpix", blank=True, null=True, default=80
    )
    pay_to_ypixel = models.IntegerField(
        db_column="nPayToYpix", blank=True, null=True, default=710
    )
    amt_num_xpixel = models.IntegerField(
        db_column="nAmtnumXpix", blank=True, null=True, default=410
    )
    amt_num_ypixel = models.IntegerField(
        db_column="nAmtnumYpix", blank=True, null=True, default=660
    )
    amt_txt1_xpixel = models.IntegerField(
        db_column="nAmtTxt1Xpix", blank=True, null=True, default=80
    )
    amt_txt1_ypixel = models.IntegerField(
        db_column="nAmtTxt1Ypix", blank=True, null=True, default=680
    )
    amt_txt2_xpixel = models.IntegerField(
        db_column="nAmtTxt2Xpix", blank=True, null=True, default=44
    )
    amt_txt2_ypixel = models.IntegerField(
        db_column="nAmtTxt2Ypix", blank=True, null=True, default=655
    )

    class Meta:
        #    managed = False
        db_table = "T10CHQ10"
        verbose_name = "a5.Cheque Control"

    def __str__(self) -> str:
        return f"{self.bank_name} - {self.bank_coa}"


class T10Chq11(models.Model):
    Chq_layout_id = models.ForeignKey(
        T10Chq10, models.PROTECT, db_column="IdChqLayout", null=True
    )
    chq_book_ref = models.CharField(
        db_column="sChqBookId", max_length=20, blank=True, null=True
    )
    begin_num = models.IntegerField(db_column="nChqNumBegin", blank=True, null=True)
    end_num = models.IntegerField(db_column="nChqNumEnd", blank=True, null=True)
    used_num = models.IntegerField(db_column="nChqNumUsed", default=0, null=True)
    Book_Status = models.CharField(
        max_length=5,
        db_column="sBookSts",
        choices=(("open", "open"), ("used", "used"), ("new", "new")),
        blank=True,
        null=True,
    )

    class Meta:
        #    managed = False
        db_table = "T10CHQ11"
        verbose_name = "Cheque Book"

    def __str__(self) -> str:
        return f"{self.chq_book_ref}"


class T10Chq20(models.Model):
    chq_layout_id = models.ForeignKey(
        T10Chq10, models.PROTECT, db_column="IdChq10", null=True
    )
    bpv_id = models.BigIntegerField(db_column="IdBPV", blank=True, null=True)
    chq_book_id = models.ForeignKey(
        T10Chq11, models.PROTECT, db_column="IdChq11", blank=True, null=True
    )
    chq_num = models.IntegerField(db_column="nChqNum", blank=True, null=True)
    chq_amt = models.DecimalField(
        db_column="dChqAmt", max_digits=18, decimal_places=0, blank=True, null=True
    )
    chq_status = models.CharField(
        max_length=10,
        db_column="sChqSts",
        choices=(("printed", "printed"), ("cancelled", "cancelled")),
        default="printed",
        null=True,
    )
    status_note = models.CharField(
        db_column="sComment", max_length=50, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T10CHQ20"
        verbose_name = "Cheque Transaction"

    def __str__(self) -> str:
        return f"{self.id}"


# Prepayment Amortization (schedule)
class T10Pps10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdDivPrePay", null=True
    )
    voucher_id = models.ForeignKey(
        T10Gld10, models.PROTECT, db_column="IdVocPrePay", null=True
    )
    prepay_coa = models.ForeignKey(
        T10Gld11, models.PROTECT, db_column="IdCoaPre", null=True
    )
    prepay_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="dPrePayAmt", blank=True, null=True
    )
    allocated_coa = models.ForeignKey(
        T01Coa10, models.PROTECT, db_column="IdAlloCoa", null=True
    )
    FREQUENCY_CHOICES = (
        ("monthly", "monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "yearly"),
    )
    frequency = models.CharField(
        max_length=10, db_column="sfrequency", null=True, choices=FREQUENCY_CHOICES
    )
    prepay_schedule_from = models.DateField(db_column="dtPreScheduleFr", null=True)
    prepay_months = models.FloatField(db_column="dPreMonth", blank=True, null=True)
    allocated_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="dAllowAmt", blank=True, null=True
    )
    STATUS_CHOICES = (("active", "Active"), ("closed", "Closed"))
    status = models.CharField(
        max_length=10, db_column="sStatus", choices=STATUS_CHOICES, default="active"
    )
    allocated_dt = models.DateField(db_column="dtAlloc", blank=True, null=True)
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="sGLCode", null=True
    )

    class Meta:
        verbose_name = "p9.Prepayment Schedule"
        ordering = ["prepay_schedule_from"]

    def clean(self):
        super(T10Pps10, self).clean()
        # Checking for voucher_id, prepay_coa already exists
        if (
            self._state.adding
            and T10Pps10.objects.filter(
                voucher_id=self.voucher_id, prepay_coa=self.prepay_coa
            ).exists()
        ):
            raise forms.ValidationError(
                f"Schdule with this ({self.voucher_id}, {self.prepay_coa}) already exists."
            )

    def save(self, *args, **kwargs):
        if self._state.adding:
            pre_coa = self.prepay_coa
            self.prepay_amt = (
                pre_coa.bcurr_debit
                if pre_coa.bcurr_debit not in [None, 0, 0.00]
                else pre_coa.bcurr_credit
            )

            # Calculate next schedule date as per frequency
            if self.frequency == "monthly":
                frequented_month = 1
            elif self.frequency == "quarterly":
                frequented_month = 3
            else:
                frequented_month = 12

            self.allocated_amt = Decimal(self.prepay_amt) / Decimal(
                self.prepay_months / frequented_month
            )
            super().save(*args, **kwargs)

            # After save, create another rows depend on the frequency and prepay_months
            T10Pps10_list = []
            next_prepay_schedule_from = self.prepay_schedule_from

            for i in range(1, int(self.prepay_months / frequented_month)):
                next_prepay_schedule_from = next_prepay_schedule_from + relativedelta(
                    months=frequented_month
                )
                T10Pps10_list.append(
                    T10Pps10(
                        division=self.division,
                        voucher_id=self.voucher_id,
                        prepay_coa=self.prepay_coa,
                        prepay_amt=self.prepay_amt,
                        allocated_coa=self.allocated_coa,
                        frequency=self.frequency,
                        prepay_months=self.prepay_months,
                        allocated_amt=self.allocated_amt,
                        gl_code=self.gl_code,
                        prepay_schedule_from=next_prepay_schedule_from,
                    )
                )
            T10Pps10.objects.bulk_create(T10Pps10_list)

    def prepayment_posting(self):
        try:
            mapping_data = {
                field.name: self.__getattribute__(field.name)
                for field in self._meta.fields
            }
            mapping_data.update({"vou_date": self.voucher_id.vou_date})
            gl_ids = T10Gld10.auto_gl_post(
                self.gl_code.id, self.prepay_coa.base_curr, mapping_data
            )

            if gl_ids:
                # Update the value of prepayment invoice
                T10Pps10.objects.filter(id=self.id).update(
                    allocated_dt=date.today(), status="closed"
                )
                return 1
        except Exception as e:
            raise ValueError(e)
