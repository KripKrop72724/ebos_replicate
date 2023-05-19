from django.conf import settings

from ebos2201.models.m01_core_mas import T01Cfg10
from ebos2210.views.v10_voc_types_handler import Vouchers
from ebos2201.utils import get_path


def gl_voucher_print(instance):
    new_tab = False

    file_pdf = Vouchers.voc_type_print(
        voucher=instance,
        lineItems=instance.gld_header_set.all(),
        company=instance.division.company,
        print_option=instance.vou_type.print_header,
        prg_type=instance.vou_type.voucher_name.prg_type,
    )

    file_url = f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file_pdf}"

    # Check the configuration for print in new tab
    if get_conf_details := T01Cfg10.objects.filter().last():
        if get_conf_details.display_print_in_new_tab:
            new_tab = True

    return file_url, new_tab
