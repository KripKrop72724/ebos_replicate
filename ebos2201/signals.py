from django.db.models.signals import pre_save
from django.dispatch import receiver

from ebos2201.models.m01_core_mas import T01Voc12, T01VocC12


# call function when click on save button of T01Voc12
@receiver(pre_save, sender=T01VocC12)
def trigger_on_save_T01VocC12(sender, instance, **kwargs):
    if instance.voucher_type != None and instance.year_num != None:
        T01Voc12.open_period(instance)
    else:
        print("Mandatory fields are empty")
