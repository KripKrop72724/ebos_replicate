from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django import forms
from django.db import models

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2210.models.m10_fin_link import T10Tib10

from .m10_fin_ap import T10Ppd10
from .m10_fin_gl import T10Alc10, T10Alc11, T10Alc12, T10Gld10

# Account receieveable

# Receivable Invoice (Debit Note)
class T10Dbn10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Dbn10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="DBN")
        )


class T10Dbn10(T10Gld10):
    objects = T10Dbn10Manager()

    class Meta:
        proxy = True
        verbose_name = "r4.Debit Note"


# Account Receivable Invoice
class T10Ari10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Ari10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="ARI")
        )


class T10Ari10(T10Gld10):
    objects = T10Ari10Manager()

    class Meta:
        proxy = True
        verbose_name = "r1.Receivable Invoice"


# Allocated Receipt vocuher
class T10Arv10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Arv10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="ARV")
        )


class T10Arv10(T10Alc10):
    object = T10Arv10Manager()

    class Meta:
        proxy = True
        verbose_name = "r8.Allocate and Receive"
        verbose_name_plural = "r8.Allocate and Receive"

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


# Receipt vouchers
# Bank RECEIPT Voucher
class T10Brv10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Brv10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="BRV")
        )


class T10Brv10(T10Gld10):
    objects = T10Brv10Manager()

    class Meta:
        proxy = True
        verbose_name = "r5.Bank Receipt Voucher"


# Cash RECEIPT Voucher
class T10Crv10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Crv10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="CRV")
        )


class T10Crv10(T10Gld10):
    objects = T10Crv10Manager()

    class Meta:
        proxy = True
        verbose_name = "r6.Cash Receipt Voucher"


# PDC Recievable Review proxy
class T10Rpd10Manager(models.Manager):
    def get_queryset(self):
        return super(T10Rpd10Manager, self).get_queryset().filter(pdc_code="ar")


class T10Rpd10(T10Ppd10):
    objects = T10Rpd10Manager()

    class Meta:
        proxy = True
        verbose_name = "r7.PDC Recievable Review"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.pdc_code = "ar"
            super(T10Rpd10, self).save(*args, **kwargs)
            self.import_PDC_data()


# Receipt allocation
class T10Ral10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Ral10Manager, self)
            .get_queryset()
            .filter(vou_type__voucher_name__prg_type="RAL")
        )


class T10Ral10(T10Alc10):
    object = T10Ral10Manager()
    ar_allocation_prg = str

    class Meta:
        verbose_name = "r9.Receipt Allocation"


# Receivables projection
# class T10Rpr10(models.Model):
#     class Meta:
#         verbose_name = "Receivables Projection"


# Tax Invoice AR header proxy
class T10Tir10Manager(models.Manager):
    def get_queryset(self):
        return (
            super(T10Tir10Manager, self)
            .get_queryset()
            .filter(inv_type__voucher_name__prg_type="TIR")
        )


class T10Tir10(T10Tib10):
    objects = T10Tir10Manager()

    class Meta:
        proxy = True
        verbose_name = "r2.Tax Invoice Receivable"


# Recurring Sales invoice
class T10Rin10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdDivRin", null=True
    )
    invoice = models.ForeignKey(T10Tib10, models.PROTECT, db_column="IdInv", null=True)
    FREQUENCY_CHOICES = (
        ("monthly", "monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "yearly"),
    )
    frequency = models.CharField(
        max_length=10, db_column="sfrequency", null=True, choices=FREQUENCY_CHOICES
    )
    recurring_from = models.DateField(db_column="dtRecurrFrom", null=True)
    contract_months = models.FloatField(db_column="dContractMnt", null=True)
    STATUS_CHOICES = (
        ("active", "Active"),
        ("closed", "Closed"),
        ("terminated", "Terminated"),
    )
    status = models.CharField(
        max_length=10, db_column="sStatus", choices=STATUS_CHOICES, default="active"
    )
    allocated_dt = models.DateField(db_column="dtAllocInv", blank=True, null=True)

    class Meta:
        verbose_name = "r3.Recurring Invoice"
        ordering = ("recurring_from",)

    def clean(self):
        super(T10Rin10, self).clean()
        # Checking for division, invoice already exists
        if (
            self._state.adding
            and T10Rin10.objects.filter(
                division=self.division, invoice=self.invoice
            ).exists()
        ):
            raise forms.ValidationError(
                f"Invoice with this ({self.division}, {self.invoice}) already exists."
            )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.invoice.recurring_status == True:
                self.recurring_from = self.invoice.inv_date

                # Calculate next invoice date as per frequency
                if self.frequency == "monthly":
                    frequented_month = 1
                elif self.frequency == "quarterly":
                    frequented_month = 3
                else:
                    frequented_month = 12

            super().save(*args, **kwargs)
            # Update recurring id on T10Tib10
            T10Tib10.objects.filter(id=self.invoice.id).update(recurr_id=self.id)

            # After save, create another rows depend on the frequency and contract_months
            T10Rin10_list = []
            next_recurring_from = self.recurring_from

            for i in range(1, int(self.contract_months / frequented_month)):
                next_recurring_from = next_recurring_from + relativedelta(
                    months=frequented_month
                )
                T10Rin10_list.append(
                    T10Rin10(
                        division=self.division,
                        invoice=self.invoice,
                        frequency=self.frequency,
                        contract_months=self.contract_months,
                        recurring_from=next_recurring_from,
                    )
                )
            T10Rin10.objects.bulk_create(T10Rin10_list)

    def gernerate_recurring_invoice(self):
        try:
            invoice_obj = self.invoice
            number_of_days_to_pay = invoice_obj.due_date - invoice_obj.inv_date
            new_due_date = self.recurring_from + timedelta(
                days=number_of_days_to_pay.days
            )

            T10Tib10.objects.create(
                division=invoice_obj.division,
                inv_type=invoice_obj.inv_type,
                inv_date=self.recurring_from,
                due_date=new_due_date,
                inv_curr=invoice_obj.inv_curr,
                hdr_ref=invoice_obj.hdr_ref,
                hdr_comment=invoice_obj.hdr_comment,
                subledger=invoice_obj.subledger,
                pmt_term=invoice_obj.pmt_term,
                gl_code=invoice_obj.gl_code,
                recurring_status=invoice_obj.recurring_status,
                recurr_id=invoice_obj.recurr_id,
            )

            # Update the value of recurring invoice
            T10Rin10.objects.filter(id=self.id).update(
                allocated_dt=date.today(), status="closed"
            )

            return 1
        except Exception as e:
            raise ValueError(e)
