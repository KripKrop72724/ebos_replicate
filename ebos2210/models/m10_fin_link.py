from datetime import date, datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import F, Sum

from ebos2201.models.m01_core_mas import (
    T01Com10,
    T01Cur10,
    T01Cur11,
    T01Div10,
    T01Uom10,
    T01Voc11,
    T01Voc12,
)
from ebos2201.models.m01_fin_mas import T01Coa10, T01Glc10, T01Sld10
from ebos2201.utils import get_fin_period


class T10Wor10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDWoDiv", null=True
    )
    wo_code = models.CharField(
        db_column="sWoCode", max_length=10, blank=True, null=True
    )
    wo_name = models.CharField(
        db_column="sWoName", max_length=300, blank=True, null=True
    )
    wo_num = models.BigIntegerField(db_column="nJobNo", blank=True, null=True)
    coa = models.BigIntegerField(db_column="IDCOA10", blank=True, null=True)
    sub_ledger = models.BigIntegerField(
        db_column="IDAddressBook", blank=True, null=True
    )
    wo_address = models.CharField(
        db_column="sAddr1", max_length=50, blank=True, null=True
    )
    actual_value = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fActValue", blank=True, null=True
    )
    estimated_value = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fEstValue", blank=True, null=True
    )
    wo_status = models.SmallIntegerField(db_column="nStatus", blank=True, null=True)
    warehouse = models.BigIntegerField(db_column="IDWhs10", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T10WOR10"
        verbose_name = "a3.Work Order"
        ordering = ["wo_name"]

    def __str__(self) -> str:
        return f"{self.division} - {self.wo_code}"


class T10Pst10(models.Model):
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="sGLCode", null=True
    )
    aa_code = models.IntegerField(db_column="nAACode", null=True)
    system_code = models.CharField(
        db_column="sSysNum", max_length=2, blank=True, null=True
    )
    description = models.CharField(db_column="sDesc", max_length=30, blank=True)
    vou_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="sVocType", null=True, blank=True
    )
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IDPstDiv", null=True
    )
    hdr_ref_field = models.CharField(
        db_column="sAmtField", max_length=50, blank=True, null=True
    )
    hdr_comment1_dict = models.CharField(
        db_column="sGldComment1", max_length=60, blank=True, null=True
    )
    hdr_comment2_dict = models.CharField(
        db_column="sGldComment2", max_length=60, blank=True, null=True
    )

    class Meta:
        db_table = "T10PST10"
        verbose_name = "a1.Posting Control"
        unique_together = ("gl_code", "aa_code")  # gl_code + aa_code is unique

    def __str__(self) -> str:
        return f"{self.gl_code}, {str(self.aa_code)}"


class T10Pst11(models.Model):
    # each AAcode generate one voucher
    aa_code = models.ForeignKey(
        T10Pst10,
        models.PROTECT,
        db_column="nAACode",
        related_name="pst_setup",
        null=True,
    )
    amount_field = models.CharField(
        db_column="sAmtField", max_length=20, blank=True
    )  # net_pay
    coa_code = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdCOA",
        null=True,
        limit_choices_to={"coa_control": "2"},
    )
    flag_db_cr = models.CharField(
        db_column="sDbCrFlag",
        max_length=2,
        blank=True,
        choices=(("db", "DB"), ("cr", "CR")),
    )  # DB, CR
    subledger_field = models.CharField(
        db_column="sSLField", max_length=20, blank=True, null=True
    )
    voc_narration_dict = models.CharField(
        db_column="sVouComment", max_length=80, blank=True
    )
    allocation_flag = models.BooleanField(db_column="bAlloc", null=True)

    class Meta:
        #    managed = False
        db_table = "T10PST11"
        verbose_name = "Posting Setup"

    def __str__(self) -> str:
        return f"{self.aa_code}"


class T10Gld10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdGldDiv", null=True
    )
    vou_num = models.BigIntegerField(db_column="nVocNum", default=0)
    vou_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="sVocType", max_length=2
    )
    vou_date = models.DateField(db_column="dVocDate", default=date.today)
    comment1 = models.CharField(
        db_column="sGLDcomment1", max_length=180, blank=True, null=True
    )
    comment2 = models.CharField(
        db_column="sGLDcomment2", max_length=180, blank=True, null=True
    )
    vou_curr = models.ForeignKey(
        T01Cur10, models.PROTECT, db_column="sBaseCurr", blank=True, null=True
    )  # auto from T01Div10
    subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdSubLed", blank=True, null=True
    )
    MDP_CHOICE = (("1", "Online"), ("2", "Cheque"), ("3", "Cash"), ("4", "Credit Card"))
    mode_of_pay = models.CharField(
        db_column="sModOfPay", max_length=1, default="1", choices=MDP_CHOICE
    )
    issued_to = models.CharField(
        db_column="sIssuedTo", max_length=40, blank=True, null=True
    )
    issued_ref = models.CharField(
        db_column="sIssuedRef", max_length=50, blank=True, null=True
    )
    # date_due = models.DateField(db_column='dDueDate', blank=True, null=True)
    vou_hdr_ref = models.CharField(
        db_column="sHdrRef", max_length=10, blank=True, null=True
    )
    GLDSTATUS_CHOICE = (("1", "Entered"), ("2", "Approved"), ("3", "On-Hold"))
    voc_status = models.CharField(
        db_column="sVoc_status", max_length=1, choices=GLDSTATUS_CHOICE, default="1"
    )
    auto_entry_flag = models.BooleanField(
        db_column="bAutoEntry", blank=True, null=True, default=False
    )  # auto update from T01Voc11
    delete_flag = models.BooleanField(
        db_column="bDeleted", default=False, blank=True, null=True
    )
    post_flag = models.BooleanField(
        db_column="bPosted", default=False, blank=True, null=True
    )  # auto update
    total_amount = models.DecimalField(
        db_column="dTotalAmt",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        blank=True,
        null=True,
    )
    paid_flag = models.BooleanField(db_column="bPaidFlag", default=False)
    email_sent_flag = models.BooleanField(db_column="bSentFlag", default=False)

    class Meta:
        #    managed = False
        db_table = "T10GLD10"
        verbose_name = "GL Voucher Header"
        ordering = ("vou_num",)

    def __str__(self) -> str:
        return f"{self.vou_type} - {self.vou_date}"

    @property
    def gld11_set(self):
        return self.gld_header_set.all()

    @property
    def gld12_set(self):
        return self.gld12_details_set.all()

    @property
    def amount(self):
        return f"{self.total_amount} {self.vou_curr}"

    def gl_bal_update(vou_num, vou_type, vou_date, delete_opt, post_opt):
        try:
            t10gld10_obj = T10Gld10.objects.get(
                vou_type=vou_type,
                vou_num=vou_num,
                vou_date=vou_date,
                delete_flag=delete_opt,
            )

            # Check `alloc_amt_tot` == 0
            if (
                post_opt == False
                and t10gld10_obj.gld_header_set.exclude(
                    alloc_amt_tot=Decimal(0.00)
                ).exists()
            ):
                raise ValueError("Voucher cannot unpost.")

            if delete_opt == True or post_opt == False:
                calc = "-"
            elif post_opt == True:
                calc = "+"
            if (vou_date) == "str":
                vou_date = datetime.strptime(vou_date, "%Y-%m-%d")  # '2021-05-21'
            for t10gld11_obj in t10gld10_obj.gld_header_set.all():
                if t10gld11_obj.vou_coa.coa_control == "2":
                    amount = t10gld11_obj.bcurr_debit - t10gld11_obj.bcurr_credit
                    # update coa balance
                    T10Abs10.update_coa_balance(
                        coa_id=t10gld11_obj.vou_coa,
                        year=vou_date.year,
                        vou_period=vou_date.month,
                        calc=calc,
                        vou_amount=amount,
                        vou_type=vou_type,
                    )

                    # update sl balance
                    T10Sbs10.update_sl_balance(
                        subledger_id=t10gld11_obj.vou_subledger,
                        year=vou_date.year,
                        vou_period=vou_date.month,
                        calc=calc,
                        vou_amount=amount,
                        vou_type=vou_type,
                    )
            t10gld10_obj.post_flag = post_opt
            t10gld10_obj.delete_flag = delete_opt
            t10gld10_obj.save()
        except Exception as e:
            raise ValueError("No record found in Gl post with this value.")

    def post_voucher(voc_num, voc_type, vou_date):
        # call this function only for posting gl vouchers and T10Gld10.post_flag = False
        # Example: Direct voucher entry into T10Gld10 and T10Gld11 (JVM, BPV, CPV etc.)
        T10Gld10.gl_bal_update(
            voc_num, voc_type, vou_date, delete_opt=False, post_opt=True
        )

    def unpost_voucher(voc_num, voc_type, vou_date):
        # call this function only for unpost gl vouchers and T10Gld10.post_flag = True
        # Example: Direct voucher unpost in the T10Gld10 and T10Gld11 (JVM, BPV, CPV etc.)
        T10Gld10.gl_bal_update(
            voc_num, voc_type, vou_date, delete_opt=False, post_opt=False
        )

    def auto_gl_post(
        gl_code: int, vou_curr: object, line_obj_dict: dict, gld12_obj_list: list = None
    ):
        # Call this function to create voucher from other modules
        # Example: Tax invoice, Fixed asset posting, Motor policy, Payroll posting
        try:
            vou_date = line_obj_dict["vou_date"]
            if (vou_date) == "str":
                vou_date = datetime.strptime(vou_date, "%Y-%m-%d")
            year = vou_date.year
            period = vou_date.month

            t10pst10_objs = T10Pst10.objects.filter(gl_code__id=gl_code)

            if t10pst10_objs.exists():
                gld_obj = None
                gl_ids = []

                # Insert data into T10GLD10
                for t10pst10_obj in t10pst10_objs:
                    total_bcurr_debit = Decimal(0.00)
                    total_fcurr_debit = Decimal(0.00)

                    division = t10pst10_obj.division
                    hdr_ref = line_obj_dict.get(t10pst10_obj.hdr_ref_field)
                    hdr_comment1 = (
                        t10pst10_obj.hdr_comment1_dict.format(**line_obj_dict)
                        if t10pst10_obj.hdr_comment1_dict
                        else None
                    )
                    hdr_comment2 = (
                        t10pst10_obj.hdr_comment2_dict.format(**line_obj_dict)
                        if t10pst10_obj.hdr_comment2_dict
                        else None
                    )
                    next_num, next_num_pfx_sfx = T01Voc12.next_number(
                        t10pst10_obj.vou_type, vou_date
                    )
                    vou_num = next_num

                    gld_obj = T10Gld10.objects.create(
                        division=division,
                        vou_num=vou_num,
                        vou_type=t10pst10_obj.vou_type,
                        vou_date=vou_date,
                        comment1=hdr_comment1,
                        comment2=hdr_comment2,
                        vou_curr=vou_curr,
                        # subledger
                        # Issued_to
                        # issued_ref
                        # mode_of_pay
                        vou_hdr_ref=hdr_ref,
                        auto_entry_flag=True,
                        post_flag=True,
                    )

                    # Insert data into T10GLD11
                    for t10pst11_obj in t10pst10_obj.pst_setup.all():
                        # get the debit or credit amount
                        amount_field = t10pst11_obj.amount_field
                        if line_obj_dict.get(amount_field):
                            amount = line_obj_dict[amount_field]
                            if amount not in [None, 0, 0.00]:
                                credit, debit = 0.00, 0.00
                                if amount:
                                    if t10pst11_obj.flag_db_cr == "db":
                                        debit = amount
                                    elif t10pst11_obj.flag_db_cr == "cr":
                                        credit = amount

                                # get base_curr value
                                foreign_curr, fcurr_debit, fcurr_credit, curr_rate = (
                                    None,
                                    0.00,
                                    0.00,
                                    0,
                                )
                                if vou_curr == division.currency:
                                    base_curr = vou_curr
                                    bcurr_debit, bcurr_credit = debit, credit
                                else:
                                    base_curr, foreign_curr = (
                                        division.currency,
                                        vou_curr,
                                    )
                                    fcurr_debit, fcurr_credit = debit, credit
                                    curr_rate = T01Cur11.get_curr_rate(
                                        foreign_curr, base_curr, vou_date, "gl"
                                    )

                                    bcurr_debit = fcurr_debit * curr_rate
                                    bcurr_credit = fcurr_credit * curr_rate

                                narration = t10pst11_obj.voc_narration_dict.format(
                                    **line_obj_dict
                                )
                                subledger_field = t10pst11_obj.subledger_field
                                subledger_id = None
                                if subledger_field:
                                    subledger_id = line_obj_dict[
                                        t10pst11_obj.subledger_field
                                    ]

                                t10gld11_obj = T10Gld11.objects.create(
                                    vou_id=gld_obj,
                                    vou_period=period,
                                    vou_year=year,
                                    vou_coa=t10pst11_obj.coa_code,
                                    vou_subledger_id=subledger_id,
                                    base_curr=base_curr,
                                    bcurr_debit=bcurr_debit,
                                    bcurr_credit=bcurr_credit,
                                    foreign_curr=foreign_curr,
                                    fcurr_debit=fcurr_debit,
                                    fcurr_credit=fcurr_credit,
                                    curr_rate=curr_rate,
                                    narration=narration,
                                    # work_order=work_order,
                                    # chq_num=cheque_num,
                                    # chq_date=cheque_date,
                                    # chq_status=cheque_status,
                                    # vou_line_ref=vou_line_ref
                                )

                                # update coa balance
                                T10Abs10.update_coa_balance(
                                    coa_id=t10pst11_obj.coa_code,
                                    year=year,
                                    vou_period=period,
                                    calc="+",
                                    vou_amount=amount,
                                    vou_type=t10pst10_obj.vou_type,
                                )

                                # update sl balance
                                T10Sbs10.update_sl_balance(
                                    subledger_id=t10gld11_obj.vou_subledger,
                                    year=year,
                                    vou_period=period,
                                    calc="+",
                                    vou_amount=amount,
                                    vou_type=t10pst10_obj.vou_type,
                                )
                                # Calculate the total
                                if bcurr_debit:
                                    total_bcurr_debit += Decimal(bcurr_debit)
                                if fcurr_debit:
                                    total_fcurr_debit += Decimal(fcurr_debit)

                    # Update the total amount of T10GLD10
                    if total_fcurr_debit > 0.00:
                        T10Gld10.objects.filter(id=gld_obj.id).update(
                            total_amount=total_fcurr_debit
                        )
                    elif total_bcurr_debit > 0.00:
                        T10Gld10.objects.filter(id=gld_obj.id).update(
                            total_amount=total_bcurr_debit
                        )

                    # Append the vou_num
                    gl_ids.append(gld_obj.id)

                # Insert data into T10GLD12
                if gld12_obj_list and gld_obj:
                    t10gld12_objs = []
                    for gld12_obj in gld12_obj_list:
                        t10gld12_objs.append(
                            T10Gld12(
                                vou_id=gld_obj,
                                tax_code_id=gld12_obj["tax_code"],
                                tax_booked_dt=gld12_obj["tax_booked_dt"],
                                taxable_amount=gld12_obj["taxable_amount"],
                                tax_amount=gld12_obj["tax_amount"],
                                adj_amount=gld12_obj.get("adj_amount", None),
                            )
                        )
                    T10Gld12.objects.bulk_create(t10gld12_objs)
                return gl_ids
            raise ValueError("Posting data not exists")
        except Exception as e:
            raise ValueError(f"Posting error: {e}")

    def auto_gl_unpost(gld10: object):
        # def auto_gl_unpost(voc_num:int, voc_type:object, vou_date:date, unpost_date=None):
        # Call this function to unpost voucher from other modules
        # Example: Tax invoice, Fixed asset posting, Motor policy, Payroll posting
        try:
            unpost_opt_val = gld10.vou_type.unpost_option
            delete_opt_val = gld10.vou_type.delete_option
            voc_num = gld10.vou_num 
            vou_type = gld10.vou_type
            vou_date = gld10.vou_date

            if unpost_opt_val == "delete_record":
                T10Gld10.gl_data_delete(voc_num, vou_type, vou_date, delete_opt_val)
            else:  # reverse voucher when unposted
                # if unpost_date is None: unpost_date=datetime.today().date()
                unpost_date = datetime.today().date()
                T10Gld10.gl_data_reverse(voc_num, vou_type, vou_date, unpost_date)
        except Exception as e:
            raise ValueError("Not exists the object.")

    def gl_data_delete(vou_num, vou_type, vou_date, delete_opt_val):
        try:
            t10gld10_obj = T10Gld10.objects.get(
                vou_type=vou_type, vou_num=vou_num, vou_date=vou_date
            )

            if type(vou_date) == 'str':
                vou_date = datetime.strptime(vou_date, "%Y-%m-%d")  # '2021-05-21'
            
            for t10gld11_obj in t10gld10_obj.gld_header_set.all():
                amount = t10gld11_obj.bcurr_debit - t10gld11_obj.bcurr_credit
                # update coa balance
                T10Abs10.update_coa_balance(
                    coa_id=t10gld11_obj.vou_coa,
                    year=vou_date.year,
                    vou_period=vou_date.month,
                    calc="-",
                    vou_amount=amount,
                    vou_type=vou_type,
                )

                # update sl balance
                T10Sbs10.update_sl_balance(
                    subledger_id=t10gld11_obj.vou_subledger,
                    year=vou_date.year,
                    vou_period=vou_date.month,
                    calc="-",
                    vou_amount=amount,
                    vou_type=vou_type,
                )

            if delete_opt_val != "mark_as_delete":
                t10gld10_obj.delete()
            else:
                t10gld10_obj.post_flag = False
                t10gld10_obj.delete_flag = True
                t10gld10_obj.save()
        except:
            raise ValueError("No record found in Gl post with this value.")

    def gl_data_reverse(vou_num: int, vou_type: object, vou_date: date, unpost_date):
        # get next_number by passing vou_type, unpost_date
        next_num, next_num_pfx_sfx = T01Voc12.next_number(vou_type, vou_date)
        if type(vou_date) == "str":
            vou_date = (datetime.strptime(vou_date, "%Y-%m-%d"),)  # '2021-05-21'

        try:
            t10gld10_old_obj = T10Gld10.objects.get(vou_num=vou_num, vou_type=vou_type)
            # Create new row
            values = T10Gld10.objects.values().get(vou_num=vou_num, vou_type=vou_type)
            values.pop("id")
            values.update({"vou_num": next_num, "vou_date": unpost_date})
            t10gld10_new_obj = T10Gld10.objects.create(**values)

            with transaction.atomic():
                for row in t10gld10_old_obj.gld_header_set.values():
                    row.pop("id")
                    row.update(
                        {
                            "vou_id": t10gld10_new_obj,
                            "bcurr_debit": row["bcurr_credit"],
                            "bcurr_credit": row["bcurr_debit"],
                            "fcurr_debit": row["fcurr_credit"],
                            "fcurr_credit": row["fcurr_debit"],
                            "narration": f"Reversed {row['narration']}",
                        }
                    )

                    t10gld11_new_obj = T10Gld11.objects.create(**row)
                    amount = (
                        t10gld11_new_obj.bcurr_debit - t10gld11_new_obj.bcurr_credit
                    )
                    # update coa balance
                    T10Abs10.update_coa_balance(
                        coa_id=t10gld11_new_obj.vou_coa,
                        year=vou_date.year,
                        vou_period=vou_date.month,
                        calc="-",
                        vou_amount=amount,
                        vou_type=vou_type,
                    )

                    # update sl balance
                    T10Sbs10.update_sl_balance(
                        subledger_id=t10gld11_new_obj.vou_subledger,
                        year=vou_date.year,
                        vou_period=vou_date.month,
                        calc="-",
                        vou_amount=amount,
                        vou_type=vou_type,
                    )

                    T10Gld10.objects.filter(id=t10gld11_new_obj.id).update(
                        post_flag=True, delete_flag=False
                    )
        except Exception as ex:
            raise ValueError("Gl post has no record for these values.")

    def gld_mtd_balance(
        division,
        coa_id,
        as_of_year=None,
        as_of_month=None,
        as_of_day=None,
        as_of_date=None,
    ):
        base_curr, curr_rate, debit_total, credit_total = None, 0.00, 0, 0
        curr_code_id = None

        if as_of_date:
            t10gld11_obj = T10Gld11.objects.filter(
                vou_id__division=division,
                vou_id__vou_date=as_of_date,
                vou_coa__id=coa_id,
            )
            if t10gld11_obj:
                debit_total = t10gld11_obj[0].bcurr_debit
                credit_total = t10gld11_obj[0].bcurr_credit
                base_curr, curr_rate = (
                    t10gld11_obj[0].base_curr,
                    t10gld11_obj[0].curr_rate,
                )
                curr_code_id = (T10Gld10.objects.filter(id=t10gld11_obj[0].vou_id.id))[
                    0
                ].vou_curr
        else:
            as_of_mn, as_of_yr = get_fin_period(
                datetime(as_of_year, as_of_month, 1), division.company.finyear_begin
            )
            for dates in range(1, as_of_day + 1):
                t10gld11_obj = T10Gld11.objects.filter(
                    vou_period=as_of_mn,
                    vou_year=as_of_yr,
                    vou_coa__id=coa_id,
                    vou_id__vou_date__day=dates,
                    vou_id__division=division,
                )
                if t10gld11_obj:
                    # gld_total = t10gld11_obj.aggregate(total=Sum(F('bcurr_debit')+F('bcurr_credit')))['total']
                    debit_total += t10gld11_obj[0].bcurr_debit
                    credit_total += t10gld11_obj[0].bcurr_credit
                    base_curr, curr_rate = (
                        t10gld11_obj[0].base_curr,
                        t10gld11_obj[0].curr_rate,
                    )
                    curr_code_id = (
                        T10Gld10.objects.filter(id=t10gld11_obj[0].vou_id.id)
                    )[0].vou_curr

        if curr_code_id != base_curr and curr_rate not in (0, 0.00):
            debit_total = debit_total / curr_rate
            credit_total = credit_total / curr_rate

        return debit_total, credit_total


class T10Gld11(models.Model):
    vou_id = models.ForeignKey(
        T10Gld10,
        db_column="IdGldVoc",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="gld_header_set",
    )
    vou_period = models.IntegerField(
        db_column="nPeriod", blank=True, null=True
    )  # auto from voc_date
    vou_year = models.IntegerField(
        db_column="nYear", blank=True, null=True
    )  # auto from voc_date
    vou_coa = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdGldCoa",
        blank=True,
        null=True,
        limit_choices_to={"coa_control": "2"},
    )
    vou_subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IDSubLedger", blank=True, null=True
    )
    base_curr = models.ForeignKey(
        T01Cur10,
        models.PROTECT,
        db_column="sBaseCurr",
        blank=True,
        null=True,
        related_name="gld11_BaseCurr",
    )  # auto from T01Div10
    bcurr_debit = models.DecimalField(
        db_column="fBCDebit",
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=Decimal("0.00"),
    )
    bcurr_credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fBCCredit",
        blank=True,
        default=Decimal("0.00"),
    )
    foreign_curr = models.ForeignKey(
        T01Cur10,
        models.PROTECT,
        db_column="sFCurr",
        blank=True,
        null=True,
        related_name="gld11_FCurr",
    )  # auto from T01GLD10 (header)
    fcurr_debit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fFCDebit",
        blank=True,
        null=True,
        default=Decimal("0.00"),
    )
    fcurr_credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fFCCredit",
        blank=True,
        null=True,
        default=Decimal("0.00"),
    )
    curr_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fCurrRate",
        blank=True,
        default=Decimal("0.00"),
    )  # foreign_curr is blank, curr_rate is 0
    narration = models.CharField(
        db_column="sNarration", max_length=180, blank=True, null=True
    )
    work_order = models.ForeignKey(
        T10Wor10, models.PROTECT, db_column="IdGldWor", blank=True, null=True
    )
    cc_number = models.CharField(
        db_column="sCCNo", max_length=16, blank=True, null=True
    )
    cc_expiry_date = models.DateField(db_column="dCCExp", blank=True, null=True)
    cc_auth_code = models.CharField(
        db_column="sAuthCode", max_length=10, blank=True, null=True
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
    prepared_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fPrep", blank=True, null=True
    )
    restatement_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fRtCurr", blank=True, null=True
    )
    alloc_amt_tot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="fAllocAmt",
        blank=True,
        null=True,
        default=Decimal("0.00"),
    )
    alloc_date = models.DateField(db_column="dAllocDt", blank=True, null=True)
    due_date = models.DateField(db_column="dDueDt", blank=True, null=True)
    bank_reco_id = models.BigIntegerField(db_column="IDbrc10", blank=True, null=True)
    chq_pmt_id = models.BigIntegerField(db_column="IDChq11", blank=True, null=True)
    vou_line_ref = models.CharField(
        db_column="sLineRef", max_length=130, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T10GLD11"
        verbose_name = "Voucher Detail"  # GL Voucher Detail

    def __str__(self) -> str:
        return f"{self.vou_id.vou_num}"


class T10Gld12(models.Model):
    vou_id = models.ForeignKey(
        T10Gld10,
        db_column="IdGldVoc",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="gld12_details_set",
    )
    tax_code = models.ForeignKey(
        "T10Tax10", models.PROTECT, db_column="IdTxcod", blank=True, null=True
    )
    tax_booked_dt = models.DateField(db_column="dtTxBk", default=datetime.now)
    taxable_amount = models.DecimalField(
        db_column="dTxableAmt",
        max_digits=10,
        decimal_places=2,
        default="0.00",
        blank=True,
        null=True,
    )
    tax_amount = models.DecimalField(
        db_column="dTxAmt",
        max_digits=10,
        decimal_places=2,
        default="0.00",
        blank=True,
        null=True,
    )
    adj_amount = models.DecimalField(
        db_column="dAdkAmt",
        max_digits=10,
        decimal_places=2,
        default="0.00",
        blank=True,
        null=True,
    )

    class Meta:
        #    managed = False
        db_table = "T10GLD12"
        verbose_name = "GL Tax Booking"

    def __str__(self) -> str:
        return f"{self.tax_code}-{self.tax_booked_dt}"


class T10BaseTax10(models.Model):
    tax_filling_country = models.CharField(
        max_length=3, db_column="sTxFillCty", default="UAE"
    )
    tax_code = models.IntegerField(db_column="dTxCod", unique=True)
    tax_name = models.CharField(max_length=20, db_column="sTxName", default="VAT")
    line_group = models.CharField(
        max_length=8,
        db_column="sLineGrp",
        choices=(("sales", "Sales"), ("purchase", "Purchase")),
    )
    line_description = models.CharField(
        max_length=200, db_column="sLineDes", blank=True, null=True
    )
    inv_region = models.CharField(
        max_length=50, db_column="sInvReg", blank=True, null=True
    )
    inv_country = models.CharField(
        max_length=50, db_column="sInvCty", blank=True, null=True
    )
    tax_percent = models.DecimalField(
        max_digits=10, db_column="nTaxPerc", decimal_places=2, default="0.05"
    )

    class Meta:
        abstract = True


class T10Tax10(T10BaseTax10):
    class Meta:
        db_table = "T10TAX10"
        verbose_name = "a2.Tax Setup"

    def __str__(self) -> str:
        return f"{self.tax_filling_country}-{self.tax_code}-{self.line_group}"


class T10Tax11(models.Model):
    tax_filling_country = models.CharField(
        max_length=3, db_column="sTxFillCty", default="UAE"
    )
    company = models.ForeignKey(
        T01Com10, models.PROTECT, db_column="IDComTx", null=True
    )
    tax_reg_num = models.BigIntegerField(db_column="nTxRefNum")
    tax_period_from = models.DateField(db_column="dtTxPrdFr")
    tax_period_to = models.DateField(db_column="dtTxPrdTo")
    tax_return_ref = models.CharField(
        max_length=50, db_column="sTaxRtnRef", blank=True, null=True
    )

    class Meta:
        db_table = "T10TAX11"
        verbose_name = "b2.Tax Filing"

    def __str__(self) -> str:
        return f"{self.tax_filling_country}-{self.company}-{self.tax_reg_num}"

    def import_tax_booked(self):
        # Get all T10Gld12 data based on company related division and date range
        t10gld12_objs = T10Gld12.objects.filter(
            vou_id__division__company=self.company,
            tax_booked_dt__range=[self.tax_period_from, self.tax_period_to],
        )
        print(t10gld12_objs)
        # Get tax_code and sum the fields data of T10Gld12
        for tax_setup in T10Tax10.objects.all():
            objs = t10gld12_objs.filter(tax_code=tax_setup)
            print(objs.exists())
            if objs.exists():
                total = objs.aggregate(
                    taxable_amount=Sum("taxable_amount"),
                    vat_amount=Sum("tax_amount"),
                    adj_amount=Sum("adj_amount"),
                )

                T10Tax12.objects.update_or_create(
                    tax_code=tax_setup.tax_code,
                    defaults={
                        "tax_return_ref": self,
                        "line_group": tax_setup.line_group,
                        "line_description": tax_setup.line_description,
                        "inv_region": tax_setup.inv_region,
                        "inv_country": tax_setup.inv_country,
                        **total,
                    },
                )


class T10Tax12(T10BaseTax10):
    tax_return_ref = models.ForeignKey(
        T10Tax11,
        models.PROTECT,
        db_column="IDTxCy",
        null=True,
        related_name="tax_return_set",
    )
    taxable_amount = models.DecimalField(
        db_column="dTxableAmt",
        max_digits=10,
        decimal_places=2,
        default="0.00",
        blank=True,
        null=True,
    )
    vat_amount = models.DecimalField(
        db_column="dVtAmt",
        max_digits=10,
        decimal_places=2,
        default="0.00",
        blank=True,
        null=True,
    )
    adj_amount = models.DecimalField(
        db_column="dAdkAmt",
        max_digits=10,
        decimal_places=2,
        default="0.00",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "T10TAX12"
        verbose_name = "Tax Return"

    def __str__(self) -> str:
        return f"{self.tax_filling_country}-{self.tax_code}-{self.line_group}"


# Tax return sales proxy models
class T10SalesTaxManager(models.Manager):
    def get_queryset(self):
        return super(T10SalesTaxManager, self).get_queryset().filter(line_group="sales")


class T10SalesTax(T10Tax12):
    objects = T10SalesTaxManager()

    class Meta:
        proxy = True
        verbose_name = "Sales Tax Record"


# Tax return Purchase proxy models
class T10PurchaseTaxManager(models.Manager):
    def get_queryset(self):
        return (
            super(T10PurchaseTaxManager, self)
            .get_queryset()
            .filter(line_group="purchase")
        )


class T10PurchaseTax(T10Tax12):
    objects = T10PurchaseTaxManager()

    class Meta:
        proxy = True
        verbose_name = "Purchase Tax Record"


class T10Abs10(models.Model):
    coa_id = models.ForeignKey(
        T01Coa10,
        models.PROTECT,
        db_column="IdAbsCoa",
        blank=True,
        null=True,
        limit_choices_to={"coa_control": "2"},
    )
    fin_year = models.IntegerField(db_column="nFinYear", blank=True, null=True)
    coa_opbal = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fOpnBal", blank=True, null=True
    )
    coa_p01_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP01act", blank=True, null=True
    )
    coa_p02_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP02act", blank=True, null=True
    )
    coa_p03_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP03act", blank=True, null=True
    )
    coa_p04_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP04act", blank=True, null=True
    )
    coa_p05_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP05act", blank=True, null=True
    )
    coa_p06_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP06act", blank=True, null=True
    )
    coa_p07_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP07act", blank=True, null=True
    )
    coa_p08_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP08act", blank=True, null=True
    )
    coa_p09_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP09act", blank=True, null=True
    )
    coa_p10_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP10act", blank=True, null=True
    )
    coa_p11_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP11act", blank=True, null=True
    )
    coa_p12_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP12act", blank=True, null=True
    )
    coa_audit_adj = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fAuditAdj", blank=True, null=True
    )
    coa_clbal = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fClBal", blank=True, null=True
    )
    # coa_p01_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP01bud', blank=True, null=True)
    # coa_p02_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP02bud', blank=True, null=True)
    # coa_p03_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP03bud', blank=True, null=True)
    # coa_p04_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP04bud', blank=True, null=True)
    # coa_p05_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP05bud', blank=True, null=True)
    # coa_p06_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP06bud', blank=True, null=True)
    # coa_p07_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP07bud', blank=True, null=True)
    # coa_p08_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP08bud', blank=True, null=True)
    # coa_p09_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP09bud', blank=True, null=True)
    # coa_p10_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP10bud', blank=True, null=True)
    # coa_p11_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP11bud', blank=True, null=True)
    # coa_p12_budget = models.DecimalField(max_digits=10, decimal_places=2, db_column='fP12bud', blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T10ABS10"
        verbose_name = "c1.Account Balance"

    def __str__(self) -> str:
        return f"{self.fin_year} - {self.coa_opbal} - {self.coa_clbal}"

    ##For Fetching Account Balance Summary based on Report Type
    def coa_bal_by_rpt_type(coa_id, year, month, rpt_type):
        try:
            coa_objs = T10Abs10.objects.filter(coa_id__id=coa_id, fin_year=year)
            debit, credit, temp = 0, 0, 0
            for coa_obj in coa_objs:
                coa_obj = coa_obj.__dict__

                if rpt_type == "1":
                    temp = Decimal(coa_obj["coa_opbal"] or 0.00)
                elif rpt_type == "2":
                    pre_aud_cl_bal = Decimal(
                        coa_obj["coa_opbal"] or 0.00
                    ) + T10Abs10.coa_period_cum_bal(coa_obj, 12)
                    audit_cl_bal = pre_aud_cl_bal + Decimal(
                        coa_obj["coa_audit_adj"] or 0.00
                    )
                    temp = audit_cl_bal
                elif rpt_type == "3":
                    fin_begin_month = T01Coa10.objects.get(
                        id=coa_id
                    ).division.company.finyear_begin
                    if month in range(13, 19):
                        if month == 13:
                            period = range(1, 3)
                        elif month == 14:
                            period = range(4, 6)
                        elif month == 15:
                            period = range(7, 9)
                        elif month == 16:
                            period = range(10, 12)
                        elif month == 17:
                            period = range(1, 6)
                        else:
                            period = range(7, 12)

                        for mnt in period:
                            fin_month, fin_year = get_fin_period(
                                datetime(year, mnt, 1), fin_begin_month
                            )
                            temp += T10Abs10.coa_period_cum_bal(coa_obj, fin_month)
                    else:
                        fin_month, fin_year = get_fin_period(
                            datetime(year, month, 1), fin_begin_month
                        )
                        temp = T10Abs10.coa_period_cum_bal(coa_obj, fin_month)

                # for figuring whether it is debit or credit
                if temp < 0:
                    credit = credit + temp
                else:
                    debit = debit + temp

            return str(debit), str(credit)

        except:
            raise ValueError("No record found")

    ## For Cumulative Balance
    def coa_period_cum_bal(obj, period):
        cum_bal = 0  # initialising the cumulative balance variable
        for val in range(1, period + 1):
            cum_bal += Decimal(obj[f"coa_p{val:02d}_actual"] or 0.00)
        return cum_bal

    # Calclulate the closing balance
    def coa_clbal_net(t10abs10_obj: dict):
        pre_audit_clbal = T10Abs10.coa_period_cum_bal(t10abs10_obj, 12)
        return pre_audit_clbal + Decimal(t10abs10_obj["coa_audit_adj"] or 0)

    def update_coa_balance(
        coa_id: object, year: int, vou_period: int, calc, vou_amount, vou_type
    ):  
        # update the corresponding Year + COA column,
        # If the (year + COA) unique record doesn't exist then insert new record and update
        column = "coa_audit_adj" if vou_type == "4" else f"coa_p{vou_period:02d}_actual"
        amount = 0.00

        try:
            # Udpate
            coa = T10Abs10.objects.get(coa_id=coa_id, fin_year=year)
            coa_dict = coa.__dict__
            if calc == "+":
                amount = Decimal(coa_dict[column] or 0) + Decimal(vou_amount)
            else:
                amount = Decimal(coa_dict[column] or 0) - Decimal(vou_amount)
            setattr(coa, column, amount)  # coa.coa_p05_actual=1200
            coa.coa_clbal = T10Abs10.coa_clbal_net(coa.__dict__)
            coa.save()
        except MultipleObjectsReturned:
            raise ValueError(
                "In one year, same chart of account cannot have multiple records."
            )
        except ObjectDoesNotExist:
            # New row create
            coa = T10Abs10(coa_id=coa_id, fin_year=year)
            if calc == "+":
                amount = vou_amount
            setattr(coa, column, amount)  # coa.coa_p05_actual=1200
            coa.coa_clbal = T10Abs10.coa_clbal_net(coa.__dict__)
            coa.save()

    def coa_opening_bal(coa_id: int, as_of_date, curr_code_id: int):
        as_of_day = as_of_date.day  # ['day']
        as_of_month = as_of_date.month  # ['month']
        as_of_year = as_of_date.year  # ['year']
        try:
            # Map the as of month and year with the company financial year begin
            fin_begin = T01Coa10.objects.get(id=coa_id).division.company.finyear_begin
            if fin_begin != 1:
                as_of_month, as_of_year = get_fin_period(as_of_date, fin_begin)

            coa_obj = T10Abs10.objects.filter(coa_id__id=coa_id, fin_year=as_of_year)
            abs_month = as_of_month - 1
            opening_bal = 0

            if coa_obj:
                coa_obj = coa_obj[0].__dict__
                opening_bal = Decimal(coa_obj["coa_opbal"] or 0.00)

                if abs_month != 0:
                    # opening balance + all month balance until previous month
                    for mnt in range(1, abs_month+1):
                        column = f"coa_p{mnt:02d}_actual"
                        opening_bal += Decimal(coa_obj[column] or 0.00)

            base_curr, curr_rate, gld_total = None, 0.00, 0.00
            for dates in range(1, as_of_day):
                t10gld11_obj = T10Gld11.objects.filter(
                    vou_period=as_of_month,
                    vou_year=as_of_year,
                    vou_coa__id=coa_id,
                    vou_id__vou_date__day=dates,
                    vou_id__delete_flag=False,
                    vou_id__post_flag=True,
                )
                if t10gld11_obj:
                    gld_total = t10gld11_obj.aggregate(
                        total=Sum(F("bcurr_debit") + F("bcurr_credit"))
                    )["total"]
                    print("gld_total", gld_total)
                    base_curr, curr_rate = t10gld11_obj[0].base_curr, Decimal(
                        t10gld11_obj[0].curr_rate
                    )
            bal_as_of = Decimal(opening_bal) + Decimal(gld_total)

            if curr_code_id != base_curr and curr_rate not in (0, 0.00):
                bal_as_of = bal_as_of / curr_rate
            bal_as_of = Decimal(bal_as_of)

            return bal_as_of
        except:
            return Decimal("0.00")


class T10Sbs10(models.Model):
    subledger_id = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdSbsSld", blank=True, null=True
    )
    fin_year = models.IntegerField(db_column="nFinYear", blank=True, null=True)
    sl_opbal = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fOpnBal", blank=True, null=True
    )
    sl_p01_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP01act", blank=True, null=True
    )
    sl_p02_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP02act", blank=True, null=True
    )
    sl_p03_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP03act", blank=True, null=True
    )
    sl_p04_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP04act", blank=True, null=True
    )
    sl_p05_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP05act", blank=True, null=True
    )
    sl_p06_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP06act", blank=True, null=True
    )
    sl_p07_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP07act", blank=True, null=True
    )
    sl_p08_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP08act", blank=True, null=True
    )
    sl_p09_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP09act", blank=True, null=True
    )
    sl_p10_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP10act", blank=True, null=True
    )
    sl_p11_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP11act", blank=True, null=True
    )
    sl_p12_actual = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fP12act", blank=True, null=True
    )
    sl_audit_adj = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fAuditAdj", blank=True, null=True
    )
    sl_clbal = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fClBal", blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T10SBS10"
        verbose_name = "c2.Subledger Balance"

    def __str__(self) -> str:
        return f"{self.fin_year} - {self.sl_opbal}- {self.sl_clbal}"

    ## For Cumulative Balance
    def sl_period_cum_bal(obj, period):
        cum_bal = 0  # initialising the cumulative balance variable
        for val in range(1, period + 1):
            cum_bal += Decimal(obj[f"sl_p{val:02d}_actual"] or 0.00)
        return cum_bal

    # Calclulate the closing balance
    def sl_clbal_net(t10sbs10_obj: dict):
        pre_audit_clbal = T10Sbs10.sl_period_cum_bal(t10sbs10_obj, 12)
        return pre_audit_clbal + Decimal(t10sbs10_obj["sl_audit_adj"] or 0)

    def update_sl_balance(
        subledger_id: object, year: int, vou_period: int, calc, vou_amount, vou_type
    ):
        # update the corresponding T10Sbs10 column
        column = "sl_audit_adj" if vou_type == "4" else f"sl_p{vou_period:02d}_actual"
        amount = 0.00

        try:
            # check for subledger_id and final year
            subledger = T10Sbs10.objects.get(subledger_id=subledger_id, fin_year=year)
            subledger_dict = subledger.__dict__
            if calc == "+":
                amount = Decimal(subledger_dict[column] or 0) + Decimal(vou_amount)
            else:
                amount = Decimal(subledger_dict[column] or 0) - Decimal(vou_amount)
            setattr(subledger, column, amount)  # subledger.sl_p05_actual=1200
            subledger.sl_clbal = T10Sbs10.sl_clbal_net(subledger.__dict__)
            subledger.save()
        except MultipleObjectsReturned:
            raise ValueError(
                "In one year, same subledger balance cannot store for multiple times."
            )
        except ObjectDoesNotExist:
            # New row create
            subledger = T10Sbs10(subledger_id=subledger_id, fin_year=year)
            if calc == "+":
                amount = vou_amount
            setattr(subledger, column, amount)  # subledger.sl_p05_actual=1200
            subledger.sl_clbal = T10Sbs10.sl_clbal_net(subledger.__dict__)
            subledger.save()

    def sl_opening_bal(sl_code_id: int, as_of_date, curr_id: int):
        as_of_day = as_of_date.day
        mn = as_of_date.month
        yr = as_of_date.year
        try:
            sbs_obj = T10Sbs10.objects.get(
                subledger_id__id=sl_code_id, fin_year=yr
            ).__dict__
            sbs_month = mn - 1
            if sbs_month == 0:
                previous_month_bal = sbs_obj["sl_opbal"]
            else:
                column = f"sl_p{sbs_month:02d}_actual"
                previous_month_bal = sbs_obj[column]

            base_curr, curr_rate, gld_total = None, 0.00, 0.00
            for dates in range(1, as_of_day):
                t10gld11_obj = T10Gld11.objects.filter(
                    vou_period=mn,
                    vou_year=yr,
                    vou_subledger__id=sl_code_id,
                    vou_id__vou_date__day=dates,
                )
                if t10gld11_obj:
                    gld_total = t10gld11_obj.aggregate(
                        total=Sum(F("bcurr_debit") + F("bcurr_credit"))
                    )["total"]
                    base_curr, curr_rate = (
                        t10gld11_obj[0].base_curr,
                        t10gld11_obj[0].curr_rate,
                    )

            if previous_month_bal == None:
                previous_month_bal = 0.00

            bal_as_of = Decimal(previous_month_bal) + Decimal(gld_total)

            if curr_id != base_curr and curr_rate not in (0, 0.00):
                bal_as_of = bal_as_of / curr_rate

            return bal_as_of
        except:
            return Decimal("0.00")


# Tax invoice
class T10Tib10(models.Model):
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column="IdDivTi")
    inv_curr = models.ForeignKey(
        T01Cur10, models.PROTECT, db_column="IDInvCurr", null=True
    )
    inv_type = models.ForeignKey(T01Voc11, models.PROTECT, db_column="IdVocTi")
    inv_date = models.DateField(db_column="dtInv")
    due_date = models.DateField(db_column="dtDue")
    inv_num = models.PositiveBigIntegerField(db_column="dInvNum", blank=True, null=True)
    hdr_ref = models.CharField(
        max_length=80, db_column="sHdrRef", blank=True, null=True
    )
    hdr_comment = models.CharField(
        max_length=100, db_column="sHdrCmmt", blank=True, null=True
    )
    subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdSubledger", blank=True, null=True
    )
    pmt_term = models.CharField(
        max_length=80, db_column="sPmtTerm", blank=True, null=True
    )
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="nGLCode", blank=True, null=True
    )
    recurring_status = models.BooleanField(default=False)
    recurr_id = models.IntegerField(blank=True, null=True)
    post_flag = models.BooleanField(db_column="bPstFlag", default=False)
    gl_ref = models.BigIntegerField(db_column="IdGld10", blank=True, null=True)

    class Meta:
        db_table = "T10TIB10"
        verbose_name = "Tax invoice base header"
        ordering = ("inv_num",)

    def __str__(self) -> str:
        return f"{self.inv_type} - {self.inv_date}"

    def save(self, *args, **kwargs):
        next_num, next_num_pfx_sfx = T01Voc12.next_number(self.inv_type, self.inv_date)
        self.inv_num = next_num
        self.due_date = self.inv_date
        super().save(*args, **kwargs)


class T10Tib11(models.Model):
    line_id = models.ForeignKey(
        T10Tib10, on_delete=models.CASCADE, db_column="IdLineTib"
    )
    tax_code = models.ForeignKey(T10Tax10, models.PROTECT, db_column="IdTaxCode")
    line_desc = models.CharField(
        max_length=80, db_column="sLineDesc", blank=True, null=True
    )
    line_uom = models.ForeignKey(
        T01Uom10, on_delete=models.CASCADE, db_column="IdLineUom", null=True
    )
    line_qty = models.IntegerField(db_column="sLineQty")
    line_unit_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="dLineUnitRate",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "T10TIB11"
        verbose_name = "Tax invoice base detail"

    @property
    def line_amt(self):
        return self.line_qty * Decimal.decimal(self.line_unit_rate)

    @property
    def line_tax_amt(self):
        return self.line_amt * self.tax_code.tax_percent

    @property
    def net_amount(self):
        return self.line_amt + self.line_tax_amt

    # total_line_amt, total_line_tax_amt,  total_net_amount
