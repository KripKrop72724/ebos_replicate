import os

from django.conf import settings
from django.contrib import messages  # import messages
from django.http import FileResponse, Http404

from ebos2201.models.m01_core_mas import *

# refering models
from ..models import *

# refering views
from ..views.v10_voc_types_handler import *


class VOCPrint:
    def manage_pdf(file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def initi_voc_print(vou_no, vou_type, vou_date):
        voucher = T10Gld10.objects.get(
            vou_num=vou_no, vou_type=vou_type, vou_date=vou_date
        )  # ,post_flag=True ,delete_flag=False
        lineItems = T10Gld11.objects.filter(vou_id__id=voucher.id)
        company = (T01Div10.objects.get(division_name=voucher.division)).company
        voucher_control = T01Voc11.objects.get(
            voucher_type=voucher.vou_type.voucher_type
        )
        print_option, prg_type = voucher_control.print_header, str(
            voucher_control.voucher_name.prg_type
        )
        return voucher, lineItems, company, print_option, prg_type

    def voc_print(vou_num, vou_type, vou_date):

        voucher, lineItems, company, print_option, prg_type = VOCPrint.initi_voc_print(
            vou_num, vou_type, vou_date
        )

        file_name = Vouchers.voc_type_print(
            voucher, lineItems, company, print_option, prg_type
        )

        if file_name == "":
            file_response = ""
        else:
            file_response = VOCPrint.manage_pdf(file_name)

        # returning file response as a file
        return file_response, file_name
