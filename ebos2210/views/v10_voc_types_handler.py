import io

from django.conf import settings
from django.db.models import Sum

# external packages
from num2words import num2words
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import GeneratePDF, RPTHandler

# ParentClass for all functions

EMP_HANDLERS = ["", "NULL", None]


class Vouchers:
    def voc_type_print(voucher, lineItems, company, print_option, prg_type):
        file_name = ""
        if prg_type == "JVM":
            file_name = JVPrint.jv_print(voucher, company, prg_type)
        elif prg_type == "BPV":
            file_name = BPVPrint.bpv_print(voucher, company, prg_type)
        elif prg_type == "CPV":
            file_name = CPVPrint.cpv_print(voucher, company, prg_type)
        elif prg_type == "BRV":
            file_name = RVPrint.rv_print(voucher, lineItems, company, print_option)
        elif prg_type == "CRV":
            file_name = CRVPrint.crv_print(voucher, lineItems, company, print_option)
        elif prg_type == "DBN":
            file_name = DBNPrint.dbn_print(voucher, lineItems, company, print_option)
        elif prg_type == "CRN":
            file_name = CRNPrint.crn_print(voucher, lineItems, company, print_option)
        elif prg_type == "ARI":
            file_name = ARIPrint.ari_print(voucher, lineItems, company, print_option)
        elif prg_type == "API":
            file_name = APIPrint.api_print(voucher, lineItems, company, print_option)
        return file_name

    def subledger_load(voucher):
        subledger = voucher.subledger
        if subledger in EMP_HANDLERS:
            return "", ""
        else:
            address = subledger.invoice_address1
            if subledger.invoice_address2 != "":
                address += "  " + subledger.invoice_address2
            if subledger.invoice_address3 != "":
                address += "  " + subledger.invoice_address3
            return subledger.subledger_name, address

    def manageNestedValues(parent, child):
        if parent in EMP_HANDLERS:
            return ""
        else:
            parent = parent.__dict__
            return parent[child]


# Get value from T10Gld10 and T10Gld11
def get_value(voucher, company, prg_type) -> dict:
    total = voucher.gld_header_set.aggregate(total_debit=Sum("bcurr_debit"))[
        "total_debit"
    ]
    logo = (
        f"{settings.SITE_DOMAIN}{company.logo_file_link.url}"
        if company.logo_file_link
        else None
    )

    params = {
        "prg_type": prg_type,
        "company_logo": logo,
        "company": company,
        "voucher": voucher,
        "voc_num": f"{voucher.vou_type.voucher_type} {str(voucher.vou_num)}",
        "total_in_word": f"{voucher.vou_curr.currency_code}: {num2words(total or 0).upper()} ONLY",
        "total_debit": total,
        "total_credit": voucher.gld_header_set.aggregate(
            total_credit=Sum("bcurr_credit")
        )["total_credit"],
    }

    return params


# child classes depending on the voucher type
class JVPrint:
    def jv_print(voucher, company, prg_type):
        TEMPLATE_NAME = "ebos2210/reports/t10_gl_voucher.html"
        PDF_FILE_NAME = "reports/journal_voucher.pdf"

        params = get_value(voucher, company, prg_type)
        params.update({"title": "Journal Voucher"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)


class BPVPrint:
    def bpv_print(voucher, company, prg_type):
        TEMPLATE_NAME = "ebos2210/reports/t10_payment_voucher.html"
        PDF_FILE_NAME = "reports/bank_payment_voucher.pdf"

        params = get_value(voucher, company, prg_type)
        params.update({"title": "Payment Voucher"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)


class CPVPrint:
    def cpv_print(voucher, company, prg_type):
        TEMPLATE_NAME = "ebos2210/reports/t10_payment_voucher.html"
        PDF_FILE_NAME = "reports/cash_payment_voucher.pdf"

        params = get_value(voucher, company, prg_type)
        params.update({"title": "Cash Payment Voucher"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)


class RVPrint:

    totals = {"debit": 0}

    def load_line_items(voucher, lineItems, fileobj, y_control):
        RVPrint.totals = {"debit": 0, "credit": 0}
        comment = str(voucher.comment1 or "") + " " + str(voucher.comment2 or "")
        for line in lineItems:
            if line.bcurr_debit != 0.00:
                if Vouchers.manageNestedValues((line.vou_coa), "account_name") != "":
                    fileobj.drawString(
                        30,
                        y_control,
                        Vouchers.manageNestedValues((line.vou_coa), "account_name"),
                    )
                    fileobj.drawString(
                        30, y_control - 15, str(line.narration or comment)
                    )
                    fileobj.drawString(310, y_control, str(line.vou_subledger or ""))
                    fileobj.drawString(
                        310, y_control, RPTHandler.emptyValueHandler(line.chq_num)
                    )
                    fileobj.drawString(
                        400, y_control, RPTHandler.emptyValueHandler(line.chq_date)
                    )
                    RVPrint.totals["debit"] += line.bcurr_debit
                    fileobj.drawString(
                        RPTHandler.calculate_x(550, str(line.bcurr_debit)),
                        y_control,
                        str(line.bcurr_debit),
                    )
                    y_control -= 40
                    if y_control <= 40:
                        fileobj.showPage()
                        y_control = 760
                        RVPrint.set_pdf_headers(fileobj, 800)
        fileobj.line(20, y_control, 570, y_control)
        return y_control

    def set_pdf_headers(fileobj, y_adjust):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(30, y_adjust, "Account Name")
        fileobj.drawString(310, y_adjust, "Chq/Ref #")
        fileobj.drawString(400, y_adjust, "Chq/Ref Dt")
        fileobj.drawString(530, y_adjust, "Amount")
        fileobj.line(20, y_adjust - 10, 570, y_adjust - 10)

    def rv_print(voucher, lineItems, company, print_option):

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        y_adjust = RPTHandler.set_comp_header(print_option, company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(210, 800 - y_adjust, "Receipt Voucher")
        fileobj.line(205, 790 - y_adjust, 345, 790 - y_adjust)

        # adding prefix
        voc_num = (
            RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")
            + " "
            + str(voucher.vou_num)
        )
        sub_name, sub_addr = Vouchers.subledger_load(voucher)

        # for labels
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(430, 770 - y_adjust, "Voc No    :")
        fileobj.drawString(430, 750 - y_adjust, "Voc Dt     :")
        fileobj.drawString(430, 730 - y_adjust, "Currency : ")
        fileobj.drawString(30, 710 - y_adjust, "Received with thanks from ")
        fileobj.drawString(30, 690 - y_adjust, "the sum of")
        fileobj.drawString(30, 670 - y_adjust, "Being : ")

        # values for title headers
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(490, 770 - y_adjust, RPTHandler.emptyValueHandler(voc_num))
        fileobj.drawString(
            490, 750 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_date))
        )
        fileobj.drawString(
            490,
            730 - y_adjust,
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_name"),
        )
        fileobj.drawString(160, 710 - y_adjust, str(sub_name))

        fileobj.drawString(
            90, 670 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.comment1))
        )
        fileobj.drawString(
            90,
            650 - y_adjust,
            RPTHandler.emptyValueHandler(str(voucher.comment2 or "")),
        )

        # for line items
        fileobj.line(20, 635 - y_adjust, 570, 635 - y_adjust)
        RVPrint.set_pdf_headers(fileobj, 620 - y_adjust)

        # for loading items here
        fileobj.setFont("Helvetica", 10)
        y_control = RVPrint.load_line_items(voucher, lineItems, fileobj, 590 - y_adjust)
        y_control -= 20
        fileobj.drawString(
            RPTHandler.calculate_x(550, str(RVPrint.totals["debit"])),
            y_control,
            str(RVPrint.totals["debit"]),
        )
        y_control -= 50

        # for signature refernce
        fileobj.line(40, y_control, 140, y_control)
        fileobj.line(180, y_control, 280, y_control)
        fileobj.line(460, y_control, 560, y_control)
        y_control -= 20
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(50, y_control, "Prepared By")
        fileobj.drawString(200, y_control, "Approved By")
        fileobj.drawString(480, y_control, "Recieved By")
        y_control -= 60

        totalInWords = (
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_code")
            + " :  "
            + num2words(RVPrint.totals["debit"]).upper()
            + " ONLY"
        )
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(
            45,
            y_control,
            "Note : Received amount will be accounted only after collection",
        )

        y_control -= 50

        fileobj.setFont("Helvetica", 8)
        fileobj.drawString(90, 690 - y_adjust, totalInWords)

        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(160, y_control, "Ref No")
        fileobj.drawString(210, y_control, "Ref Dt")
        fileobj.drawString(260, y_control, "Ref Amt")
        fileobj.drawString(310, y_control, "Allc Amt")
        fileobj.drawString(360, y_control, "Allc Date")
        y_control -= 20
        fileobj.line(150, y_control, 420, y_control)
        y_control -= 30
        fileobj.line(150, y_control, 420, y_control)

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/receipt_voucher.pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)


class CRVPrint:

    totals = {"debit": 0, "credit": 0}

    def load_line_items(voucher, lineItems, fileobj, y_control):
        CRVPrint.totals = {"debit": 0, "credit": 0}
        comment = str(voucher.comment1 or "") + " " + str(voucher.comment2 or "")
        for line in lineItems:
            if line.bcurr_debit != 0.00:
                if Vouchers.manageNestedValues((line.vou_coa), "account_name") != "":
                    fileobj.drawString(
                        20,
                        y_control,
                        Vouchers.manageNestedValues((line.vou_coa), "account_num"),
                    )
                    fileobj.drawString(
                        60,
                        y_control,
                        Vouchers.manageNestedValues((line.vou_coa), "account_name"),
                    )
                    fileobj.drawString(
                        60, y_control - 15, str(line.narration or comment)
                    )
                    fileobj.drawString(310, y_control, str(line.vou_subledger or ""))
                    CRVPrint.totals["debit"] += line.bcurr_debit
                    fileobj.drawString(
                        RPTHandler.calculate_x(540, str(line.bcurr_debit)),
                        y_control,
                        str(line.bcurr_debit),
                    )
                    y_control -= 40
                    if y_control <= 40:
                        fileobj.showPage()
                        y_control = 760
                        CRVPrint.set_pdf_headers(fileobj, 800)

    def set_pdf_headers(fileobj, y_adjust):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(20, y_adjust, "A/C#")
        fileobj.drawString(60, y_adjust, "Account Name")
        fileobj.drawString(310, y_adjust, "SubLedger")
        fileobj.drawString(530, y_adjust, "Amount")
        fileobj.line(20, y_adjust - 10, 570, y_adjust - 10)

    def crv_print(voucher, lineItems, company, print_option):

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        y_adjust = RPTHandler.set_comp_header(print_option, company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(210, 800 - y_adjust, "Cash Receipt Voucher")
        fileobj.line(210, 790 - y_adjust, 390, 790 - y_adjust)

        # adding prefix
        voc_num = (
            RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")
            + " "
            + str(voucher.vou_num)
        )
        sub_name, sub_addr = Vouchers.subledger_load(voucher)

        # for labels
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(455, 770 - y_adjust, "Voucher : ")
        fileobj.drawString(455, 750 - y_adjust, "Date   : ")
        fileobj.drawString(30, 770 - y_adjust, "Received with Thanks From :")
        fileobj.drawString(30, 705 - y_adjust, "Ref.#")
        fileobj.drawString(30, 685 - y_adjust, "Being : ")

        # values for title headers
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(505, 770 - y_adjust, RPTHandler.emptyValueHandler(voc_num))
        fileobj.drawString(
            500, 750 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_date))
        )
        fileobj.drawString(30, 750 - y_adjust, sub_name)
        fileobj.drawString(30, 730 - y_adjust, sub_addr)
        fileobj.drawString(
            80, 705 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_hdr_ref))
        )
        fileobj.drawString(
            80, 685 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.comment1))
        )
        fileobj.drawString(
            80,
            665 - y_adjust,
            RPTHandler.emptyValueHandler(str(voucher.comment2 or "")),
        )

        # for line items
        fileobj.line(20, 655 - y_adjust, 570, 655 - y_adjust)
        CRVPrint.set_pdf_headers(fileobj, 640 - y_adjust)

        # for loading items here
        fileobj.setFont("Helvetica", 10)
        CRVPrint.load_line_items(voucher, lineItems, fileobj, 610 - y_adjust)

        totalInWords = (
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_code")
            + " :  "
            + num2words(CRVPrint.totals["debit"]).upper()
            + " ONLY"
        )
        fileobj.line(20, 150, 570, 150)
        fileobj.drawString(
            RPTHandler.calculate_x(540, str(CRVPrint.totals["debit"])),
            130,
            str(CRVPrint.totals["debit"]),
        )

        # for signature refernce
        fileobj.line(40, 80, 140, 80)
        fileobj.line(180, 80, 280, 80)
        fileobj.line(460, 80, 560, 80)
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(50, 65, "Prepared By")
        fileobj.drawString(200, 65, "Verified By")
        fileobj.drawString(480, 65, "Approved By")

        fileobj.setFont("Helvetica", 8)
        fileobj.drawString(20, 130, totalInWords)

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/cash_receipt_voucher.pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)


class DBNPrint:

    totals = {"debit": 0}

    def load_line_items(voucher, lineItems, fileobj, y_control):
        DBNPrint.totals = {"debit": 0}
        comment = str(voucher.comment1 or "") + " " + str(voucher.comment2 or "")
        for line in lineItems:
            if Vouchers.manageNestedValues((line.vou_coa), "account_name") != "":
                fileobj.drawString(
                    35,
                    y_control,
                    Vouchers.manageNestedValues((line.vou_coa), "account_name"),
                )
                fileobj.drawString(220, y_control, str(line.narration or comment))
                DBNPrint.totals["debit"] += line.bcurr_debit
                fileobj.drawString(
                    RPTHandler.calculate_x(540, str(line.bcurr_debit)),
                    y_control,
                    str(line.bcurr_debit),
                )
                y_control -= 40
                if y_control <= 40:
                    fileobj.showPage()
                    y_control = 760
                    DBNPrint.set_pdf_headers(fileobj, 800)
        return y_control + 10

    def set_pdf_headers(fileobj, y_adjust):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(35, y_adjust, "Account Name")
        fileobj.drawString(220, y_adjust, "Description")
        fileobj.drawString(530, y_adjust, "Debit")
        fileobj.line(20, y_adjust - 10, 570, y_adjust - 10)

    def dbn_print(voucher, lineItems, company, print_option):

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        y_adjust = RPTHandler.set_comp_header(print_option, company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(240, 800 - y_adjust, "Debit Note")
        fileobj.line(230, 790 - y_adjust, 340, 790 - y_adjust)

        # adding prefix
        voc_num = (
            RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")
            + " "
            + str(voucher.vou_num)
        )
        sub_name, sub_addr = Vouchers.subledger_load(voucher)

        # for labels
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(430, 770 - y_adjust, "Voucher : ")
        fileobj.drawString(430, 750 - y_adjust, "Date   : ")
        fileobj.drawString(430, 730 - y_adjust, "Currency : ")
        fileobj.drawString(30, 750 - y_adjust, "Issued to :")
        fileobj.drawString(30, 705 - y_adjust, "Ref. No:")
        fileobj.drawString(30, 680 - y_adjust, "Being : ")
        # fileobj.drawString(30,690,"Being : ")

        # values for title headers
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(495, 770 - y_adjust, RPTHandler.emptyValueHandler(voc_num))
        fileobj.drawString(
            490, 750 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_date))
        )
        fileobj.drawString(
            490,
            730 - y_adjust,
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_name"),
        )
        fileobj.drawString(100, 750 - y_adjust, sub_name)
        fileobj.drawString(100, 730 - y_adjust, sub_addr)
        fileobj.drawString(
            100, 705 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_hdr_ref))
        )
        fileobj.drawString(
            100, 680 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.comment1))
        )
        # fileobj.drawString(80,670,RPTHandler.emptyValueHandler(str(voucher.comment2 or '')))

        fileobj.drawString(
            35,
            640 - y_adjust,
            "Please note that we have debited your account as follows.",
        )

        # for line items
        fileobj.line(20, 620 - y_adjust, 570, 620 - y_adjust)
        DBNPrint.set_pdf_headers(fileobj, 605 - y_adjust)

        # for loading items here
        fileobj.setFont("Helvetica", 10)
        y_control = DBNPrint.load_line_items(
            voucher, lineItems, fileobj, 580 - y_adjust
        )
        y_control -= 20
        fileobj.line(20, y_control, 570, y_control)
        y_control -= 20
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(20, y_control, "Amount in Words : ")
        fileobj.drawString(490, y_control, "Total : ")
        totalInWords = (
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_code")
            + " :  "
            + num2words(DBNPrint.totals["debit"]).upper()
            + " ONLY"
        )
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(
            RPTHandler.calculate_x(540, str(DBNPrint.totals["debit"])),
            y_control,
            str(DBNPrint.totals["debit"]),
        )

        fileobj.setFont("Helvetica", 8)
        fileobj.drawString(130, y_control, totalInWords)

        fileobj.line(480, y_control - 10, 570, y_control - 10)

        y_control -= 100
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(380, y_control, "For :")
        fileobj.drawString(410, y_control, company.company_name)

        fileobj.line(420, y_control - 100, 570, y_control - 100)
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(450, y_control - 115, "Authorised Signatory")

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/debit_note.pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)


class CRNPrint:

    totals = {"credit": 0}

    def load_line_items(voucher, lineItems, fileobj, y_control):
        CRNPrint.totals = {"credit": 0}
        comment = str(voucher.comment1 or "") + " " + str(voucher.comment2 or "")
        for line in lineItems:
            if Vouchers.manageNestedValues((line.vou_coa), "account_name") != "":
                fileobj.drawString(
                    35,
                    y_control,
                    Vouchers.manageNestedValues((line.vou_coa), "account_name"),
                )
                fileobj.drawString(220, y_control, str(line.narration or comment))
                CRNPrint.totals["credit"] += line.bcurr_credit
                fileobj.drawString(
                    RPTHandler.calculate_x(540, str(line.bcurr_credit)),
                    y_control,
                    str(line.bcurr_credit),
                )
                y_control -= 40
                if y_control <= 40:
                    fileobj.showPage()
                    y_control = 760
                    CRNPrint.set_pdf_headers(fileobj, 800)
        return y_control + 10

    def set_pdf_headers(fileobj, y_adjust):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(35, y_adjust, "Account Name")
        fileobj.drawString(220, y_adjust, "Description")
        fileobj.drawString(530, y_adjust, "Credit")
        fileobj.line(20, y_adjust - 10, 570, y_adjust - 10)

    def crn_print(voucher, lineItems, company, print_option):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        y_adjust = RPTHandler.set_comp_header(print_option, company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(240, 800 - y_adjust, "Credit Note")
        fileobj.line(230, 790 - y_adjust, 340, 790 - y_adjust)

        # adding prefix
        voc_num = (
            RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")
            + " "
            + str(voucher.vou_num)
        )
        sub_name, sub_addr = Vouchers.subledger_load(voucher)

        # for labels
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(430, 770 - y_adjust, "Voucher : ")
        fileobj.drawString(430, 750 - y_adjust, "Date   : ")
        fileobj.drawString(430, 730 - y_adjust, "Currency : ")
        fileobj.drawString(30, 750 - y_adjust, "Issued to :")
        fileobj.drawString(30, 705 - y_adjust, "Ref. No:")
        fileobj.drawString(30, 680 - y_adjust, "Being : ")
        # fileobj.drawString(30,690,"Being : ")

        # values for title headers
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(495, 770 - y_adjust, RPTHandler.emptyValueHandler(voc_num))
        fileobj.drawString(
            490, 750 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_date))
        )
        fileobj.drawString(
            490,
            730 - y_adjust,
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_name"),
        )
        fileobj.drawString(100, 750 - y_adjust, sub_name)
        fileobj.drawString(100, 730 - y_adjust, sub_addr)
        fileobj.drawString(
            100, 705 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_hdr_ref))
        )
        fileobj.drawString(
            100, 680 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.comment1))
        )
        # fileobj.drawString(80,670,RPTHandler.emptyValueHandler(str(voucher.comment2 or '')))

        fileobj.drawString(
            35,
            640 - y_adjust,
            "Please note that we have credited your account as follows.",
        )

        # for line items
        fileobj.line(20, 620 - y_adjust, 570, 620 - y_adjust)
        CRNPrint.set_pdf_headers(fileobj, 605 - y_adjust)

        # for loading items here
        fileobj.setFont("Helvetica", 10)
        y_control = CRNPrint.load_line_items(
            voucher, lineItems, fileobj, 580 - y_adjust
        )
        y_control -= 20
        fileobj.line(20, y_control, 570, y_control)
        y_control -= 20
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(20, y_control, "Amount in Words : ")
        fileobj.drawString(490, y_control, "Total : ")
        totalInWords = (
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_code")
            + " :  "
            + num2words(CRNPrint.totals["credit"]).upper()
            + " ONLY"
        )
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(
            RPTHandler.calculate_x(540, str(CRNPrint.totals["credit"])),
            y_control,
            str(CRNPrint.totals["credit"]),
        )

        fileobj.setFont("Helvetica", 8)
        fileobj.drawString(130, y_control, totalInWords)

        fileobj.line(480, y_control - 10, 570, y_control - 10)

        y_control -= 100
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(380, y_control, "For :")
        fileobj.drawString(410, y_control, company.company_name)

        fileobj.line(420, y_control - 100, 570, y_control - 100)
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(450, y_control - 115, "Authorised Signatory")

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/credit_note.pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)


class ARIPrint:

    totals = {"debit": 0}

    def load_line_items(voucher, lineItems, fileobj, y_control):
        ARIPrint.totals = {"debit": 0}
        comment = str(voucher.comment1 or "") + " " + str(voucher.comment2 or "")
        for line in lineItems:
            if Vouchers.manageNestedValues((line.vou_coa), "account_name") != "":
                fileobj.drawString(
                    35,
                    y_control,
                    Vouchers.manageNestedValues((line.vou_coa), "account_name"),
                )
                fileobj.drawString(220, y_control, str(line.narration or comment))
                ARIPrint.totals["debit"] += line.bcurr_debit
                fileobj.drawString(
                    RPTHandler.calculate_x(540, str(line.bcurr_debit)),
                    y_control,
                    str(line.bcurr_debit),
                )
                y_control -= 40
                if y_control <= 40:
                    fileobj.showPage()
                    y_control = 760
                    ARIPrint.set_pdf_headers(fileobj, 800)
        return y_control + 10

    def set_pdf_headers(fileobj, y_adjust):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(35, y_adjust, "Account Name")
        fileobj.drawString(220, y_adjust, "Description")
        fileobj.drawString(530, y_adjust, "Amount")
        fileobj.line(20, y_adjust - 10, 570, y_adjust - 10)

    def ari_print(voucher, lineItems, company, print_option):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        y_adjust = RPTHandler.set_comp_header(print_option, company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(180, 800 - y_adjust, "Account Recievable Invoice")
        fileobj.line(175, 790 - y_adjust, 405, 790 - y_adjust)

        # adding prefix
        voc_num = (
            RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")
            + " "
            + str(voucher.vou_num)
        )
        sub_name, sub_addr = Vouchers.subledger_load(voucher)

        # for labels
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(430, 770 - y_adjust, "Voucher : ")
        fileobj.drawString(430, 750 - y_adjust, "Date   : ")
        fileobj.drawString(430, 730 - y_adjust, "Currency : ")
        fileobj.drawString(30, 750 - y_adjust, "Customer :")
        fileobj.drawString(30, 705 - y_adjust, "Ref. No:")
        fileobj.drawString(30, 680 - y_adjust, "Being : ")
        # fileobj.drawString(30,690,"Being : ")

        # values for title headers
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(495, 770 - y_adjust, RPTHandler.emptyValueHandler(voc_num))
        fileobj.drawString(
            490, 750 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_date))
        )
        fileobj.drawString(
            490,
            730 - y_adjust,
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_name"),
        )
        fileobj.drawString(100, 750 - y_adjust, sub_name)
        fileobj.drawString(100, 730 - y_adjust, sub_addr)
        fileobj.drawString(
            100, 705 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_hdr_ref))
        )
        fileobj.drawString(
            100, 680 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.comment1))
        )
        # fileobj.drawString(80,670,RPTHandler.emptyValueHandler(str(voucher.comment2 or '')))

        fileobj.drawString(
            35,
            640 - y_adjust,
            "Please note that we have debited your account as follows.",
        )

        # for line items
        fileobj.line(20, 620 - y_adjust, 570, 620 - y_adjust)
        ARIPrint.set_pdf_headers(fileobj, 605 - y_adjust)

        # for loading items here
        fileobj.setFont("Helvetica", 10)
        y_control = ARIPrint.load_line_items(
            voucher, lineItems, fileobj, 580 - y_adjust
        )
        y_control -= 20
        fileobj.line(20, y_control, 570, y_control)
        y_control -= 20
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(20, y_control, "Amount in Words : ")
        fileobj.drawString(490, y_control, "Total : ")
        totalInWords = (
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_code")
            + " :  "
            + num2words(ARIPrint.totals["debit"]).upper()
            + " ONLY"
        )
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(
            RPTHandler.calculate_x(540, str(ARIPrint.totals["debit"])),
            y_control,
            str(ARIPrint.totals["debit"]),
        )

        fileobj.setFont("Helvetica", 8)
        fileobj.drawString(130, y_control, totalInWords)

        fileobj.line(480, y_control - 10, 570, y_control - 10)

        y_control -= 100
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(380, y_control, "For :")
        fileobj.drawString(410, y_control, company.company_name)

        fileobj.line(420, y_control - 100, 570, y_control - 100)
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(450, y_control - 115, "Authorised Signatory")

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/account_recieveable_invoice.pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)


class APIPrint:

    totals = {"credit": 0}

    def load_line_items(voucher, lineItems, fileobj, y_control):
        APIPrint.totals = {"credit": 0}
        comment = str(voucher.comment1 or "") + " " + str(voucher.comment2 or "")
        for line in lineItems:
            if Vouchers.manageNestedValues((line.vou_coa), "account_name") != "":
                fileobj.drawString(
                    35,
                    y_control,
                    Vouchers.manageNestedValues((line.vou_coa), "account_name"),
                )
                fileobj.drawString(220, y_control, str(line.narration or comment))
                APIPrint.totals["credit"] += line.bcurr_credit
                fileobj.drawString(
                    RPTHandler.calculate_x(540, str(line.bcurr_credit)),
                    y_control,
                    str(line.bcurr_credit),
                )
                y_control -= 40
                if y_control <= 40:
                    fileobj.showPage()
                    y_control = 760
                    APIPrint.set_pdf_headers(fileobj, 800)
        return y_control + 10

    def set_pdf_headers(fileobj, y_control):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(35, y_control, "Account Name")
        fileobj.drawString(220, y_control, "Description")
        fileobj.drawString(530, y_control, "Amount")
        fileobj.line(20, y_control - 10, 570, y_control - 10)

    def api_print(voucher, lineItems, company, print_option):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        y_adjust = RPTHandler.set_comp_header(print_option, company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(180, 800 - y_adjust, "Account Payable Invoice")
        fileobj.line(175, 790 - y_adjust, 385, 790 - y_adjust)

        # adding prefix
        voc_num = (
            RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")
            + " "
            + str(voucher.vou_num)
        )
        sub_name, sub_addr = Vouchers.subledger_load(voucher)

        # for labels
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(430, 770 - y_adjust, "Voucher : ")
        fileobj.drawString(430, 750 - y_adjust, "Date   : ")
        fileobj.drawString(430, 730 - y_adjust, "Currency : ")
        fileobj.drawString(30, 750 - y_adjust, "Supplier :")
        fileobj.drawString(30, 705 - y_adjust, "Ref. No:")
        fileobj.drawString(30, 680 - y_adjust, "Being : ")
        # fileobj.drawString(30,690,"Being : ")

        # values for title headers
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(495, 770 - y_adjust, RPTHandler.emptyValueHandler(voc_num))
        fileobj.drawString(
            490, 750 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_date))
        )
        fileobj.drawString(
            490,
            730 - y_adjust,
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_name"),
        )
        fileobj.drawString(100, 750 - y_adjust, sub_name)
        fileobj.drawString(100, 730 - y_adjust, sub_addr)
        fileobj.drawString(
            100, 705 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.vou_hdr_ref))
        )
        fileobj.drawString(
            100, 680 - y_adjust, RPTHandler.emptyValueHandler(str(voucher.comment1))
        )
        # fileobj.drawString(80,670,RPTHandler.emptyValueHandler(str(voucher.comment2 or '')))

        fileobj.drawString(
            35,
            640 - y_adjust,
            "Please note that we have credited your account as follows.",
        )

        # for line items
        fileobj.line(20, 620 - y_adjust, 570, 620 - y_adjust)
        APIPrint.set_pdf_headers(fileobj, 605 - y_adjust)

        # for loading items here
        fileobj.setFont("Helvetica", 10)
        y_control = APIPrint.load_line_items(
            voucher, lineItems, fileobj, 580 - y_adjust
        )
        y_control -= 20
        fileobj.line(20, y_control, 570, y_control)
        y_control -= 20
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(20, y_control, "Amount in Words : ")
        fileobj.drawString(490, y_control, "Total : ")
        totalInWords = (
            Vouchers.manageNestedValues(voucher.vou_curr, "currency_code")
            + " :  "
            + num2words(APIPrint.totals["credit"]).upper()
            + " ONLY"
        )
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(
            RPTHandler.calculate_x(540, str(APIPrint.totals["credit"])),
            y_control,
            str(APIPrint.totals["credit"]),
        )

        fileobj.setFont("Helvetica", 8)
        fileobj.drawString(130, y_control, totalInWords)

        fileobj.line(480, y_control - 10, 570, y_control - 10)

        y_control -= 100
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(380, y_control, "For :")
        fileobj.drawString(410, y_control, company.company_name)

        fileobj.line(420, y_control - 100, 570, y_control - 100)
        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(450, y_control - 115, "Authorised Signatory")

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/account_payable_invoice.pdf"

        return RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)
