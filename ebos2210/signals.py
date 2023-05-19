import os

from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from ebos2201.models.m01_core_mas import T01Cat10, T01Div10
from ebos2210.models.m10_fin_ap import T10Apv10
from ebos2210.models.m10_fin_ar import T10Arv10, T10Ral10
from ebos2210.models.m10_fin_fa import T10Avr01, T10Dar01, T10Fam10, T10Far01, T10Fat10
from ebos2210.models.m10_fin_gl import (
    T10AgRpt01,
    T10Alc10,
    T10Bs01,
    T10BsDt01,
    T10ChrAcc01,
    T10CshFlow01,
    T10Ctb01,
    T10Dbk01,
    T10Gla10,
    T10Glc01,
    T10Glr01,
    T10Glr02,
    T10GlrB01,
    T10LdgAcc01,
    T10Pl01,
    T10PlDt01,
    T10SlCoa01,
    T10SlCoa02,
    T10Stm01,
    T10Stm02,
    T10Tb01,
    T10Tbc01,
    T10TbDt01,
)
from ebos2210.utils.u10_gl_bl import gl_balance
from ebos2210.utils.u10_glr_bl import glr_balance
from ebos2210.views.v10_asset_valuation_report import AValuation
from ebos2210.views.v10_disposed_asset_report import DAReport

from ebos2201.utils import get_path


# Perform action before delete of proxy model T10Gla10, T10Apv10 & T10Arv10
@receiver(pre_delete, sender=T10Alc10)
@receiver(pre_delete, sender=T10Gla10)
@receiver(pre_delete, sender=T10Apv10)
@receiver(pre_delete, sender=T10Arv10)
def update_allocation(sender, instance, using, **kwargs):
    if instance.alloc_lock_flag:
        T10Alc10.unpost_allocation(instance)


# Perform action after save of proxy model T10Gla10
@receiver(post_save, sender=T10Ral10)
def proxy_T10Ral10(sender, instance, **kwargs):
    module = "AR"
    T10Alc10.create_alloc_hdr(instance, module)


# Perform action after save of Model T10GLR01
@receiver(models.signals.post_save, sender=T10GlrB01)
@receiver(models.signals.post_save, sender=T10Glc01)
@receiver(models.signals.post_save, sender=T10Stm01)
@receiver(models.signals.post_save, sender=T10Stm02)
@receiver(models.signals.post_save, sender=T10Dbk01)
@receiver(models.signals.post_save, sender=T10SlCoa01)
@receiver(models.signals.post_save, sender=T10SlCoa02)
@receiver(models.signals.post_save, sender=T10LdgAcc01)
@receiver(models.signals.post_save, sender=T10ChrAcc01)
@receiver(models.signals.post_save, sender=T10AgRpt01)
def glr01_balance(sender, instance, **kwargs):
    file_name_pdf, file_name_csv = gl_balance(instance)
    T10Glr01.objects.filter(id=instance.id).update(
        file_pdf=file_name_pdf, file_csv=file_name_csv
    )

    return True


# Perform action after save of Model T10GLR02
@receiver(models.signals.post_save, sender=T10Tb01)
@receiver(models.signals.post_save, sender=T10Bs01)
@receiver(models.signals.post_save, sender=T10Pl01)
@receiver(models.signals.post_save, sender=T10Tbc01)
@receiver(models.signals.post_save, sender=T10Ctb01)
@receiver(models.signals.post_save, sender=T10CshFlow01)
@receiver(models.signals.post_save, sender=T10TbDt01)
@receiver(models.signals.post_save, sender=T10BsDt01)
@receiver(models.signals.post_save, sender=T10PlDt01)
def glr02_balance(sender, instance, **kwargs):
    file_name_pdf, file_name_csv = glr_balance(instance)
    # Update File Fields
    T10Glr02.objects.filter(id=instance.id).update(
        file_csv=file_name_csv, file_pdf=file_name_pdf
    )

    return True


# delete files when record delete from model...
@receiver(models.signals.post_delete, sender=T10Glr01)
@receiver(models.signals.post_delete, sender=T10Glr02)
@receiver(models.signals.post_delete, sender=T10GlrB01)
@receiver(models.signals.post_delete, sender=T10Glc01)
@receiver(models.signals.post_delete, sender=T10Tb01)
@receiver(models.signals.post_delete, sender=T10Bs01)
@receiver(models.signals.post_delete, sender=T10Pl01)
@receiver(models.signals.post_delete, sender=T10Tbc01)
@receiver(models.signals.post_delete, sender=T10TbDt01)
@receiver(models.signals.post_delete, sender=T10BsDt01)
@receiver(models.signals.post_delete, sender=T10PlDt01)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file_csv:
        if os.path.isfile(instance.file_csv.path):
            os.remove(instance.file_csv.path)
    if instance.file_pdf:
        if os.path.isfile(instance.file_pdf.path):
            os.remove(instance.file_pdf.path)


@receiver(models.signals.post_save, sender=T10Fat10)
def update_T10Fam10(sender, instance, **kwargs):
    if instance.gl_code.description == "Scrap":
        T10Fam10.objects.filter(id=instance.asset_id).update(
            salvage_amt=instance.salvage_amt, asset_status=3
        )
    elif instance.gl_code.description == "Disposed":
        T10Fam10.objects.filter(id=instance.asset_id).update(
            disposal_amt=instance.disposal_amt,
            disposal_dt=instance.doc_date,
            asset_status=2,
        )


@receiver(models.signals.post_save, sender=T10Avr01)
@receiver(models.signals.post_save, sender=T10Dar01)
def far01_balance(sender, instance, **kwargs):
    far01_balance = T10Far01.objects.filter(id=instance.id)

    categories = []
    for asse_cat in T01Cat10.objects.all():
        categories.append(asse_cat)
    categories.append(None)

    if far01_balance.filter(rpt_code="FAM").exists():
        name = "asset_valuation"
        asset_records = []
        for category in categories:
            record_info = {"category": category, "records": []}
            record_info["records"] = T10Fam10.objects.filter(
                division=instance.division, asset_cat=category, asset_status="1"
            )
            asset_records.append(record_info)
        pdf_data = AValuation.export_as_val_pdf(
            T01Div10.get_div_comp(instance.division), asset_records
        )
        csv_data = AValuation.export_as_val_csv()

    elif far01_balance.filter(rpt_code="DAR").exists():
        name = "disposed_assets"
        asset_records = []
        for category in categories:
            record_info = {"category": category, "records": []}
            record_info["records"] = T10Fam10.objects.filter(
                ~Q(asset_status="1"), division=instance.division, asset_cat=category
            )
            asset_records.append(record_info)
        pdf_data = DAReport.export_dis_pdf(
            T01Div10.get_div_comp(instance.division), asset_records
        )
        csv_data = DAReport.export_dis_csv()

    # to keep only one copy of every instance
    pdf_file_name = get_path(f"reports/{name}_{str(instance.id)}.pdf")
    csv_file_name = get_path(f"reports/{name}_{str(instance.id)}.xlsx")

    if default_storage.exists(csv_file_name):
        default_storage.delete(csv_file_name)
    file_name = default_storage.save(csv_file_name, csv_data)

    if default_storage.exists(pdf_file_name):
        default_storage.delete(pdf_file_name)
    file_name_pdf = default_storage.save(pdf_file_name, pdf_data)

    # Update File Fields
    far01_balance.update(file_csv=file_name, file_pdf=file_name_pdf)

    return True
