##for file handling
import io
import os

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404
from num2words import num2words

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import RPTHandler

from ..models.m10_fin_ap import *
from ..models.m10_fin_link import *

EMP_HANDLERS = ["", "NULL", None]


class CHQLayout:
    def manage_pdf(file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def changeFormat(date):
        day = date.day
        if day < 10:
            day = "0" + str(day)
        month = date.month
        if month < 10:
            month = "0" + str(month)
        year = date.year
        date_format = str(day) + " / " + str(month) + " / " + str(year)
        return date_format

    # for maintaining empty values
    def emptyValueHandler(value):
        if value in EMP_HANDLERS:
            return 0
        else:
            return value

    def render_cheque(fileobj, layout, voucher, vou_item, margin):
        fileobj.line(30, 785 + margin, 520, 785 + margin)
        fileobj.line(30, 560 + margin, 520, 560 + margin)
        fileobj.line(30, 785 + margin, 30, 560 + margin)
        fileobj.line(520, 785 + margin, 520, 560 + margin)

        # fileobj.drawInlineImage('documents/images/logos/logo_1.png',40,735,30,30)
        fileobj.setFont("Helvetica", 12)
        fileobj.drawString(230, 570 + margin, "1234  5678  9012")
        fileobj.drawString(40, 750 + margin, "Bank Name")
        fileobj.setFont("Helvetica", 9)
        # fileobj.drawString(70,740,"Dubai")

        fileobj.setFont("Helvetica", 9)

        fileobj.drawString(
            CHQLayout.emptyValueHandler(layout.date_xpixel),
            CHQLayout.emptyValueHandler(layout.date_ypixel + margin),
            CHQLayout.changeFormat(voucher.vou_date),
        )
        fileobj.line(380, 745 + margin, 510, 745 + margin)

        fileobj.drawString(450, 710 + margin, "OR BEARER")
        fileobj.line(40, 705 + margin, 510, 705 + margin)
        fileobj.drawString(
            CHQLayout.emptyValueHandler(layout.pay_to_xpixel),
            CHQLayout.emptyValueHandler(layout.pay_to_ypixel + margin),
            str(voucher.issued_to),
        )
        if vou_item.bcurr_debit != 0.00 and vou_item.bcurr_debit != None:
            chq_amount = vou_item.bcurr_debit
        else:
            chq_amount = vou_item.bcurr_credit

        fileobj.drawString(
            CHQLayout.emptyValueHandler(layout.amt_txt1_xpixel),
            CHQLayout.emptyValueHandler(layout.amt_txt1_ypixel + margin),
            str(num2words(chq_amount).upper() + " ONLY"),
        )
        # fileobj.drawString(CHQLayout.emptyValueHandler(layout.amt_txt2_xpixel),CHQLayout.emptyValueHandler(layout.amt_txt2_ypixel),'Amount2')
        fileobj.drawString(
            CHQLayout.emptyValueHandler(layout.amt_num_xpixel),
            CHQLayout.emptyValueHandler(layout.amt_num_ypixel + margin),
            str(chq_amount) + " /-",
        )
        fileobj.drawString(100, 616 + margin, str(vou_item.vou_coa))

        fileobj.setFont("Helvetica-Bold", 9)
        fileobj.drawString(380, 750 + margin, "DATE")
        fileobj.drawString(40, 710 + margin, "Pay")
        fileobj.drawString(40, 680 + margin, "DHIRAM")
        fileobj.drawString(375, 660 + margin, "AED")
        fileobj.drawString(55, 616 + margin, "A/C No.")
        fileobj.line(40, 675 + margin, 510, 675 + margin)
        fileobj.line(40, 650 + margin, 510, 650 + margin)
        fileobj.line(510, 675 + margin, 510, 650 + margin)
        fileobj.line(400, 675 + margin, 400, 650 + margin)
        fileobj.line(370, 675 + margin, 370, 650 + margin)
        fileobj.line(390, 590 + margin, 500, 590 + margin)

        fileobj.setFont("Helvetica", 7)
        fileobj.drawString(
            340, 770 + margin, "VALID FOR THREE MONTHS FROM DATE OF ISSUE"
        )
        fileobj.drawString(400, 580 + margin, "AUTHORISED SIGNATURE")
        fileobj.drawString(230, 595 + margin, "Payable at par at all branches")
        fileobj.drawString(410, 735 + margin, "D D  /  M M  / Y Y Y Y")

        fileobj.line(50, 630 + margin, 220, 630 + margin)
        fileobj.line(50, 610 + margin, 220, 610 + margin)
        fileobj.line(50, 630 + margin, 50, 610 + margin)
        fileobj.line(90, 630 + margin, 90, 610 + margin)
        fileobj.line(220, 630 + margin, 220, 610 + margin)

    def init_pdf(request, voucher, flag=None):

        buffer = io.BytesIO()

        fileobj = canvas.Canvas(buffer)

        voucher_items = T10Gld11.objects.filter(
            vou_id=voucher, vou_coa__account_type="2"
        )

        chq_layout = None
        box_margin = 0

        for vou_item in voucher_items:
            try:
                chq_layout = T10Chq10.objects.get(bank_coa=vou_item.vou_coa)
                if vou_item.chq_pmt_id == None or vou_item.chq_pmt_id == "":
                    chq_trn_amt = CHQLayout.render_cheque(
                        fileobj, chq_layout, voucher, vou_item, box_margin
                    )
                    box_margin -= 300
                    chq_trn = T10Chq20.objects.create(
                        chq_layout_id=chq_layout,
                        bpv_id=voucher.id,
                        chq_amt=chq_trn_amt,
                        chq_status="printed",
                        status_note="",
                    )
                    vou_item.chq_pmt_id = chq_trn.id
                    vou_item.save()
                else:
                    msg = "Cheque Already Printed. Please Cancel Cheque to print it again."
                    if flag:
                        raise ValueError(msg)
                    return messages.error(request, msg)
            except T10Chq10.DoesNotExist:
                msg = "Cheque Layout is not defined."
                if flag:
                    raise ValueError(msg)
                return messages.info(request, msg)

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        # clearing out the global data holders

        PDF_FILE_NAME = "reports/cheque_layout" + str(voucher.id) + ".pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)

    def cancel_pdf(request, voucher):

        voucher_items = T10Gld11.objects.filter(
            vou_id=voucher, vou_coa__account_type="2"
        )

        for vou_item in voucher_items:
            try:
                if vou_item.chq_pmt_id != None:
                    chq_trn = T10Chq20.objects.get(id=vou_item.chq_pmt_id)
                    chq_trn.chq_status = "cancelled"
                    chq_trn.save()
                    # making chq_pmt_id in gld11 as blannk
                    vou_item.chq_pmt_id = None
                    vou_item.save()
                    return messages.success(request, "Cheque Cancellation completed")
            except T10Chq20.DoesNotExist:
                pass
