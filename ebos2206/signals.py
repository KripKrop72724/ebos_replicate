import os

from django.core.files.storage import default_storage
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ebos2201.models.m01_core_mas import T01Atm10
from ebos2206.models.m06_emp_mas import T06Dex10
from ebos2206.models.m06_hr_trn import T06Eos10, T06Wps10, T06Wps11
from ebos2206.models.m06_prl_trn import T06Hrr01, T06Hrr02
from ebos2206.utils.u06_prl_trn import PrintPrlCk, PrintPSlip

from ebos2201.utils import get_path


# Perform action after save of proxy T01Eml10 (model)
@receiver(post_save, sender=T06Dex10)
def post_save_T06Dex10(sender, instance, **kwargs):
    pdf_data = T06Dex10.emp_doc_exp_report(instance)
    # Delete file if already exists with same name
    name = "emp_document_expiry"
    pdf_file_name = f"{name}_{str(instance.id)}.pdf"

    pdf_file_name = get_path(pdf_file_name)

    # Delete if report exist with same name
    if default_storage.exists(pdf_file_name):
        default_storage.delete(pdf_file_name)

    file_name_pdf = default_storage.save(pdf_file_name, pdf_data)

    # Update File Fields
    T06Dex10.objects.filter(id=instance.id).update(report_file=file_name_pdf)
    if instance.email_code:
        T01Atm10.auto_email(instance.email_code, instance.report_file)
    return True


# Perform action after save of T06Wps10
@receiver(post_save, sender=T06Wps10)
def execute_get_wps_com_data(sender, instance, **kwargs):
    T06Wps10.get_wps_com_data(instance)
    T06Wps11.get_wps_emp_data(instance)


@receiver(post_delete, sender=T06Wps10)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.sif_file_name:
        if os.path.isfile(instance.sif_file_name.path):
            os.remove(instance.sif_file_name.path)
    else:
        print("No file")


# Perform action after save of proxy T06Eos10 (model)
@receiver(post_save, sender=T06Eos10)
def execute_insert_T06Eos10(sender, instance, **kwargs):
    T06Eos10.insert_T06Eos10(instance)


# Perform action after save of proxy T06Hrr01
@receiver(post_save, sender=T06Hrr01)
def T06Hrr01_prnt_payroll_checklist(sender, instance, **kwargs):
    PrintPrlCk(instance)
    return True


# Perform action after save of proxy T06Hrr02
@receiver(post_save, sender=T06Hrr02)
def T06Hrr02_print_payslip(sender, instance, **kwargs):
    PrintPSlip(instance)
