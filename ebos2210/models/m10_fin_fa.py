from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.forms import ValidationError

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import T01Glc10, T01Sld10
from ebos2201.utils import get_last_day_of_month
from ebos2210.models.m10_fin_gl import T10Gld10

# from ..utils import *
# from ..views import *

# fixed asset


class T10Fam10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="idDivFam", null=True
    )
    department = models.ForeignKey(
        T01Dep10, models.PROTECT, db_column="sDeptFam", blank=True, null=True
    )
    warehouse_id = models.ForeignKey(
        T01Whm10, models.PROTECT, db_column="IDwhFam", blank=True, null=True
    )
    asset_desc = models.CharField(
        db_column="sFamDesc", max_length=50, blank=True, null=True
    )
    asset_pur_doc = models.CharField(
        db_column="sPurDoc", max_length=15, blank=True, null=True
    )
    asset_pur_date = models.DateField(db_column="dPurDt", blank=True, null=True)
    asset_qty = models.IntegerField(
        db_column="fAssetQty", default=1, blank=True, null=True
    )
    # e.g: 10-chairs as one asset_tag / one part_no / serial_num_range
    serial_no = models.CharField(
        db_column="sSlNo", max_length=20, blank=True, null=True
    )
    part_no = models.CharField(
        db_column="sPartNo", max_length=20, blank=True, null=True
    )
    asset_tag_ref = models.CharField(
        db_column="sTagRef", max_length=20, blank=True, null=True
    )
    DEP_TYPE_CHOCES = (("1", "Stright Line"), ("2", "Diminishing Value"))
    dep_type = models.CharField(
        max_length=1,
        db_column="sDepType",
        choices=DEP_TYPE_CHOCES,
        blank=True,
        null=True,
    )
    life_months = models.IntegerField(db_column="nLifeMonths", blank=True, null=True)
    dep_start_dt = models.DateField(db_column="dDepSt", blank=True, null=True)
    dep_end_dt = models.DateField(db_column="dDepEnd", blank=True, null=True)
    dep_months = models.IntegerField(db_column="ndepMonths", blank=True, null=True)
    # count of how many months depreciated so far.
    dep_frequency = models.CharField(
        max_length=7,
        db_column="sdepfreq",
        choices=(("daily", "Daily"), ("monthly", "Monthly")),
        blank=True,
        null=True,
    )
    dep_percent = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fDepPerc", blank=True, null=True
    )  # % yearly for Diminishing Value method only
    asset_value = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fAstValue", blank=True, null=True
    )
    salvage_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fSalvage", blank=True, null=True
    )  # end of life value
    last_dep_dt = models.DateField(db_column="dLastDep", blank=True, null=True)
    accum_dep = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fAccumDep", blank=True, null=True
    )
    current_value = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fCurrentVal", blank=True, null=True
    )  # asset_value-accum_dep
    disposal_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fDisposeAmt", blank=True, null=True
    )
    disposal_dt = models.DateField(db_column="dDispose", blank=True, null=True)
    final_dep = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fFinalDep", blank=True, null=True
    )
    # depreciation from last_dep_dt upto disposal_dt if asset disposed before end of life.
    amc_cost = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fAmcCost", blank=True, null=True
    )  # used for Diminishing Value method only
    remarks = models.CharField(
        db_column="sRemarks", max_length=60, blank=True, null=True
    )
    last_maint_dt = models.DateField(db_column="dLastmaint", blank=True, null=True)
    next_maint_dt = models.DateField(db_column="dNextMaint", blank=True, null=True)
    amc_renew_dt = models.DateField(db_column="dAmcRenew", blank=True, null=True)
    warranty_exp_dt = models.DateField(db_column="dWarrExp", blank=True, null=True)
    ASSET_STATUS_CHOICES = (("1", "Inventory"), ("2", "Scrap"), ("3", "Disposed"))
    asset_status = models.CharField(
        db_column="sStatus",
        max_length=1,
        choices=ASSET_STATUS_CHOICES,
        default=1,
        blank=True,
    )
    subledger = models.ForeignKey(
        T01Sld10, models.PROTECT, db_column="IdSubledger", blank=True, null=True
    )
    asset_cat = models.ForeignKey(
        T01Cat10, models.PROTECT, db_column="IdFamCat", blank=True, null=True
    )  # based COA classification
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="nGLCode", blank=True, null=True
    )

    class Meta:
        db_table = "T10FAM10"
        verbose_name = "t1.Asset Master"

    def __str__(self) -> str:
        return f"{self.division}"

    def save(self, *args, **kwargs):
        if self.current_value in [0, 0.00]:
            self.current_value = self.asset_value

        return super().save(*args, **kwargs)


class T10Fam11(models.Model):
    asset_id = models.ForeignKey(
        T10Fam10,
        models.DO_NOTHING,
        db_column="IDFAM10",
        blank=True,
        null=True,
        related_name="asset_depreciation",
    )
    dep_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fDepAmt", blank=True, null=True
    )
    dep_from_dt = models.DateField(db_column="dDepFrom", blank=True, null=True)
    dep_to_dt = models.DateField(db_column="dDepTo", blank=True, null=True)
    post_flag = models.BooleanField(
        db_column="bPost", default=False, blank=True, null=True
    )
    gl_ref = models.BigIntegerField(db_column="IdGld10", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T10FAM11"
        verbose_name = "Asset Depreciation Master"

    # def __str__(self) -> str:
    #     return f"{self.asset_code}"


class T10Fam12(models.Model):
    asset_id = models.ForeignKey(
        T10Fam10, models.DO_NOTHING, db_column="IDFAM10", blank=True, null=True
    )
    last_srv_dt = models.DateField(db_column="dLastSer", blank=True, null=True)
    next_srv_dt = models.DateField(db_column="dNextSer", blank=True, null=True)
    last_calibr_dt = models.DateField(db_column="dLsstCalibr", blank=True, null=True)
    next_calibr_dt = models.DateField(db_column="dNextCalibr", blank=True, null=True)
    calibr_freq = models.CharField(
        db_column="sCaliFreq", max_length=20, blank=True, null=True
    )
    reading_before_calibr = models.CharField(
        db_column="sRdgBfrCali", max_length=25, blank=True, null=True
    )
    reading_after_calibr = models.CharField(
        db_column="sRdgAftrCali", max_length=25, blank=True, null=True
    )
    serviced_by = models.CharField(
        db_column="sSrvBy", max_length=30, blank=True, null=True
    )
    comment = models.CharField(
        db_column="scomment", max_length=60, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T10FAM12"
        verbose_name = "Asset Service Master"

    # def __str__(self) -> str:
    #     return f"{self.}"


class T10Srv10(T10Fam10):
    class Meta:
        proxy = True
        verbose_name = "t3.Asset Service"


class T10Fap10(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="idDivDep", null=True
    )
    year = models.IntegerField(db_column="nDepYear", null=True)
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
    )
    month = models.IntegerField(db_column="nDepMonth", choices=MONTH_CHOICE, null=True)
    status = models.CharField(
        max_length=8,
        db_column="sStatus",
        choices=(("posted", "Posted"), ("unposted", "Unposted")),
        default="unposted",
    )

    class Meta:
        db_table = "T10FAP10"
        verbose_name = "t5.Fixed Asset Posting"

    def post_depreciation(self):
        try:
            dep_from = date(self.year, self.month, 1)
            dep_to = get_last_day_of_month(dep_from)
            t10fam10_objs = T10Fam10.objects.prefetch_related(
                "asset_depreciation"
            ).filter(division=self.division, last_dep_dt__range=[dep_from, dep_to])
            asset_cat_dict = {}
            for asset in t10fam10_objs:
                variable_name = asset.asset_cat.category_code
                variable_amount = asset.asset_depreciation.filter(
                    post_flag=False
                ).annotate(dep_amt_total=models.Sum("dep_amt"))
                if variable_name in asset_cat_dict:
                    variable_amount += asset_cat_dict[variable_name]

                asset_cat_dict.update({variable_name: variable_amount})

                # call the post_fa_transaction()
                [
                    T10Fat10.post_fa_transaction(t10fat10_obj)
                    for t10fat10_obj in T10Fat10.objects.filter(
                        asset_id=asset, post_flag=False
                    )
                ]

            gl_ids = T10Gld10.auto_gl_post(
                t10fam10_objs[0].gl_code.id, self.division.currency, asset_cat_dict
            )
            if gl_ids[0]:
                t10fam10_objs.update(
                    asset_depreciation__post_flag=True,
                    asset_depreciation__gl_ref=gl_ids[0],
                )
            return True
        except Exception as ex:
            return False

    def unpost_depreciation(self):
        try:
            dep_from = date(self.year, self.month, 1)
            dep_to = get_last_day_of_month(dep_from)
            t10fam10_objs = T10Fam10.objects.prefetch_related(
                "asset_depreciation"
            ).filter(division=self.division, last_dep_dt__range=[dep_from, dep_to])

            for asset in t10fam10_objs:
                # unpost for T10Fam11
                t10fam11_objs = asset.asset_depreciation.filter(post_flag=True)
                for gl_ref in set([fam11.gl_ref for fam11 in t10fam11_objs]):
                    gld10_obj = T10Gld10.objects.get(id=gl_ref)
                    T01Voc11.objects.filter(voucher_type=gld10_obj.voc_type).update(
                        unpost_option="delete_record"
                    )
                    T10Gld10.auto_gl_unpost(gld10_obj)

                t10fam11_objs.update(post_flag=False, gl_ref=0)

                # call the unpost_fa_transaction()
                [
                    T10Fat10.unpost_fa_transaction(t10fat10_obj)
                    for t10fat10_obj in T10Fat10.objects.filter(
                        asset_id=asset, post_flag=True
                    )
                ]

            return True
        except Exception as ex:
            return False

    def compute_depreceiation(self, asset: object, dep_to):
        if asset.dep_type == str(1):
            monthly_dep = (
                Decimal(asset.asset_value) - Decimal(asset.salvage_amt)
            ) / Decimal(asset.life_months)
        else:
            monthly_dep = (
                Decimal(asset.current_value) + (Decimal(asset.amc_cost) / Decimal(12))
            ) * (Decimal(asset.dep_percent) / Decimal(12))

        daily_dep = Decimal(monthly_dep) / Decimal(dep_to.day)
        return (monthly_dep, daily_dep)

    def depreciation_run(self, asset: object, dep_from, dep_to):
        (monthly_amt, daily_amt) = self.compute_depreceiation(asset, dep_to)
        last_run_dt = asset.asset_depreciation.aggregate(Max("dep_to_dt"))[
            "dep_to_dt__max"
        ]
        date_from = (
            (last_run_dt + timedelta(days=1)) if last_run_dt else asset.dep_start_dt
        )

        if asset.dep_frequency == "daily":
            date_to = date_from
            dep_amt = daily_amt
        elif asset.dep_frequency == "monthly":
            date_from = date_from + timedelta(month=1)
            date_to = get_last_day_of_month(date_from)
            dep_amt = monthly_amt

        # Insert new row on T10Fam11
        [
            T10Fam11.objects.create(
                asset_id=asset,
                dep_amt=dep_amt,
                dep_from_dt=(date_from + timedelta(days=i)).strftime("%Y-%m-%d"),
                dep_to_dt=date_to,
            )
            for i in range((dep_to - date_from).days + 1)
        ]

        # Update asset master T10Fam10
        asset.last_dep_dt = dep_to
        asset.accum_dep += dep_amt
        asset.current_value = asset.asset_value - asset.accum_dep
        asset.dep_months += 1
        asset.save()


class T10Dpn10(T10Fap10):
    class Meta:
        proxy = True
        verbose_name = "t2.Asset Depreciation"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        dep_from = date(self.year, self.month, 1)
        dep_to = get_last_day_of_month(dep_from)

        [
            self.depreciation_run(asset, dep_from, dep_to)
            for asset in T10Fam10.objects.prefetch_related("asset_depreciation").filter(
                asset_status=1, last_dep_dt__range=[dep_from, dep_to]
            )
        ]


class T10Fat10(models.Model):
    asset_id = models.ForeignKey(
        T10Fam10,
        models.DO_NOTHING,
        db_column="IDFAM10",
        blank=True,
        null=True,
        related_name="asset_transaction",
    )
    doc_type = models.ForeignKey(
        T01Voc11, models.PROTECT, db_column="sDocType", blank=True, null=True
    )
    doc_num = models.BigIntegerField(db_column="nFatDoc", blank=True, null=True)
    doc_date = models.DateField(db_column="dFatDoc", blank=True, null=True)
    narration = models.CharField(
        db_column="sNarration", max_length=40, blank=True, null=True
    )
    gl_code = models.ForeignKey(
        T01Glc10, models.PROTECT, db_column="nGLCode", blank=True, null=True
    )
    disposal_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fDisposeAmt", blank=True, null=True
    )
    salvage_amt = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="fSalvageAmt", blank=True, null=True
    )
    issued_division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="idDivIssue", null=True
    )
    issued_department = models.ForeignKey(
        T01Dep10, models.PROTECT, db_column="sDeptIssue", blank=True, null=True
    )
    issued_warehouse = models.ForeignKey(
        T01Whm10, models.PROTECT, db_column="IDwhIssue", blank=True, null=True
    )
    issue_qty = models.IntegerField(db_column="nIssueQty", blank=True, null=True)
    expected_return_dt = models.DateField(db_column="dExpRet", blank=True, null=True)
    recv_division = models.ForeignKey(
        T01Div10,
        models.PROTECT,
        db_column="idDivRecv",
        related_name="recv_div",
        null=True,
    )
    recv_department = models.ForeignKey(
        T01Dep10,
        models.PROTECT,
        db_column="sDeptRecv",
        related_name="recv_dep",
        blank=True,
        null=True,
    )
    recv_warehouse = models.ForeignKey(
        T01Whm10,
        models.PROTECT,
        db_column="IDwhRecv",
        related_name="recv_wh",
        blank=True,
        null=True,
    )
    recv_qty = models.IntegerField(db_column="nRecvQty", blank=True, null=True)
    actual_return_dt = models.DateField(db_column="dActRet", blank=True, null=True)
    project_id = models.BigIntegerField(db_column="IDPrj10", blank=True, null=True)
    post_flag = models.BooleanField(
        db_column="bPost", default=False, blank=True, null=True
    )
    gl_ref = models.BigIntegerField(db_column="IdGld10", blank=True, null=True)

    class Meta:
        #    managed = False
        db_table = "T10FAT10"
        verbose_name = "t4.Asset Transaction"

    def __str__(self) -> str:
        return f"{self}"

    def post_fa_transaction(self):
        try:
            mapping_data = {
                field.name: self.__getattribute__(field.name)
                for field in self._meta.fields
            }

            if self.salvage_amt in [None, 0, 0.00]:
                mapping_data.pop("salvage_amt")
            if self.disposal_amt in [None, 0, 0.00]:
                mapping_data.pop("dispoal_amt")

            gl_ids = T10Gld10.auto_gl_post(
                self.gl_code.id, self.asset_id.division.currency, mapping_data
            )
            self.gl_ref = gl_ids[0]
            self.post_flag = True
            self.save()
        except Exception as e:
            raise ValidationError(e)

    def unpost_fa_transaction(self):
        try:
            gld10_obj = T10Gld10.objects.get(id=self.gl_ref)
            T01Voc11.objects.filter(voucher_type=gld10_obj.voc_type).update(
                unpost_option="delete_record"
            )
            T10Gld10.auto_gl_unpost(gld10_obj)

            self.gl_ref = 0
            self.post_flag = False
            self.save()
        except Exception as e:
            raise ValidationError(e)

    def save(self, *args, **kwargs):
        next_num, next_num_pfx_sfx = T01Voc12.next_number(self.doc_type, self.doc_date)
        self.doc_num = next_num
        super().save(*args, **kwargs)


class T10Vah10(T10Fam10):
    class Meta:
        proxy = True
        verbose_name = "t6.View Asset History"


class T10BaseFar01(models.Model):
    division = models.ForeignKey(
        T01Div10, models.PROTECT, db_column="IdFarDiv", null=True
    )
    file_csv = models.FileField(
        upload_to="reports/",
        max_length=250,
        null=True,
        db_column="fFarCsv",
        blank=True,
        default=None,
    )
    file_pdf = models.FileField(
        upload_to="reports/",
        max_length=250,
        null=True,
        db_column="fFarPdf",
        blank=True,
        default=None,
    )

    class Meta:
        abstract = True


# Asset Reports
class T10Far01(T10BaseFar01):
    rpt_code = models.CharField(
        db_column="sRptCode", max_length=3, blank=True, null=True
    )

    class Meta:
        db_table = "T10Far01"
        verbose_name = "FAR Primary Model 01"


# Asset Valuation Report
class T10Avr01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Avr01Manager, self).get_queryset().filter(rpt_code="FAM")


class T10Avr01(T10Far01):
    objects = T10Avr01Manager()

    class Meta:
        proxy = True
        verbose_name = "t7.Asset Valuation"

    def save(self, *args, **kwargs):
        self.rpt_code = "FAM"
        super(T10Avr01, self).save(*args, **kwargs)


# Disposed Asset Report
class T10Dar01Manager(models.Manager):
    def get_queryset(self):
        return super(T10Dar01Manager, self).get_queryset().filter(rpt_code="DAR")


class T10Dar01(T10Far01):
    objects = T10Dar01Manager()

    class Meta:
        proxy = True
        verbose_name = "t8.Disposed Asset"

    def save(self, *args, **kwargs):
        self.rpt_code = "DAR"
        super(T10Dar01, self).save(*args, **kwargs)
