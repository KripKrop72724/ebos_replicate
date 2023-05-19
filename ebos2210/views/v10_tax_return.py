##for file handling
import io
import os

from django.conf import settings
from django.http import FileResponse, Http404

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2210.models.m10_fin_link import T10Tax12
from ebos2210.utils.u10_rpt_handler import RPTHandler


class TaxReturnRpt:

    totals = {
        "sales": {"vat_total": 0, "adj_total": 0},
        "purchase": {"vat_total": 0, "adj_total": 0},
    }

    grand_totals = {"sales_grand_total": 0, "purchase_grand_total": 0, "net_total": 0}

    index = 1

    # generation of report headers
    def set_pdf_headers(fileobj, y_axis, prefix):
        fileobj.setFont("Helvetica-Bold", 9)
        fileobj.drawString(30, y_axis - 10, "No.")
        fileobj.drawString(60, y_axis - 10, "Line Description")
        fileobj.drawString(300, y_axis, "Amount")
        fileobj.drawString(305, y_axis - 15, "(AED)")
        if prefix != "":
            fileobj.drawString(400, y_axis + 15, "Recoverable")
        fileobj.drawString(400, y_axis, "VAT Amount")
        fileobj.drawString(415, y_axis - 15, "(AED)")
        fileobj.drawString(500, y_axis, "Adjustment")
        fileobj.drawString(520, y_axis - 15, "(AED)")
        fileobj.line(20, y_axis - 30, 570, y_axis - 30)

    def manage_pdf(file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def render_records(fileobj, y_axis, group, company):
        records = T10Tax12.objects.filter(
            line_group=group, tax_return_ref__company=company
        )
        if records.count() > 0:
            fileobj.setFont("Helvetica", 9)
            for rec in records:
                fileobj.drawString(30, y_axis, str(TaxReturnRpt.index))
                fileobj.drawString(60, y_axis, str(rec.line_description))
                fileobj.drawString(
                    RPTHandler.calculate_x(340, str(rec.taxable_amount)),
                    y_axis,
                    str(rec.taxable_amount),
                )
                fileobj.drawString(
                    RPTHandler.calculate_x(440, str(rec.vat_amount)),
                    y_axis,
                    str(rec.vat_amount),
                )
                fileobj.drawString(
                    RPTHandler.calculate_x(540, str(rec.adj_amount)),
                    y_axis,
                    str(rec.adj_amount),
                )
                TaxReturnRpt.totals[group]["vat_total"] += rec.vat_amount
                TaxReturnRpt.totals[group]["adj_total"] += rec.adj_amount
                y_axis -= 20
                TaxReturnRpt.index += 1
                if y_axis <= 40:
                    fileobj.showPage()
                    y_axis = 760
                    prefix = ""
                    if group == "purchase":
                        prefix = "Recoverable"
                    TaxReturnRpt.set_pdf_headers(fileobj, y_axis, prefix)
            y_axis = TaxReturnRpt.set_totals(fileobj, y_axis - 10, group)
        else:
            fileobj.setFont("Helvetica-Bold", 10)
            fileobj.drawString(240, y_axis - 10, "No Records Found")
            y_axis -= 40
        return y_axis

    def set_totals(fileobj, y_axis, group):
        fileobj.setFont("Helvetica-Bold", 9)
        fileobj.drawString(60, y_axis, "Totals:")
        fileobj.drawString(
            RPTHandler.calculate_x(440, str(TaxReturnRpt.totals[group]["vat_total"])),
            y_axis,
            "%.2f" % float(TaxReturnRpt.totals[group]["vat_total"]),
        )
        fileobj.drawString(
            RPTHandler.calculate_x(540, str(TaxReturnRpt.totals[group]["adj_total"])),
            y_axis,
            "%.2f" % float(TaxReturnRpt.totals[group]["adj_total"]),
        )
        return y_axis - 20

    def set_total_sequence(y_range, header_sequence, total_sequence, fileobj):
        index = 0
        for seq in header_sequence:
            fileobj.setFont("Helvetica", 9)
            fileobj.drawString(30, y_range, str(TaxReturnRpt.index))
            fileobj.drawString(60, y_range, str(seq))
            temp_value = TaxReturnRpt.grand_totals[total_sequence[index]]
            if index < 3:
                fileobj.drawString(
                    RPTHandler.calculate_x(340, str(temp_value)),
                    y_range,
                    "%.2f" % float(temp_value),
                )
            else:
                fileobj.drawString(330, y_range, str(temp_value))
            y_range -= 20
            index += 1
            TaxReturnRpt.index += 1
            if y_range <= 20:
                fileobj.showPage()
                y_range = 760

    def initPDF(company, reference, tax_period_from):

        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        TaxReturnRpt.index = 1
        TaxReturnRpt.totals = {
            "sales": {"vat_total": 0, "adj_total": 0},
            "purchase": {"vat_total": 0, "adj_total": 0},
        }
        TaxReturnRpt.grand_totals = {
            "sales_grand_total": 0,
            "purchase_grand_total": 0,
            "net_total": 0,
        }

        y_adjust = RPTHandler.set_comp_header(True, company, fileobj)

        fileobj.setFont("Helvetica", 15)
        fileobj.drawString(210, 730, "Tax Return Report")
        fileobj.line(210, 720, 335, 720)

        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(30, 700, "VAT Return Period  : ")
        fileobj.drawString(30, 675, "Tax Year : ")
        fileobj.drawString(250, 680, "VAT Return Period Reference Number : ")
        fileobj.drawString(30, 640, "VAT on Sales and all other Outputs ")

        vat_reference = (
            RPTHandler.emptyValueHandler(tax_period_from.month)
            + " - "
            + RPTHandler.emptyValueHandler(reference)
        )
        fileobj.setFont("Helvetica", 10)
        fileobj.drawString(
            135, 700, RPTHandler.emptyValueHandler(tax_period_from.month)
        )
        fileobj.drawString(90, 675, RPTHandler.emptyValueHandler(tax_period_from.year))
        fileobj.drawString(450, 680, str(vat_reference))

        fileobj.line(20, 630, 570, 630)
        TaxReturnRpt.set_pdf_headers(fileobj, 610, "")
        y_control = TaxReturnRpt.render_records(fileobj, 560, "sales", company)

        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(30, y_control - 20, "VAT on Expenses and all other Inputs ")

        y_control -= 40

        fileobj.line(20, y_control, 570, y_control)
        y_control -= 30
        TaxReturnRpt.set_pdf_headers(fileobj, y_control, "Recoverable")
        y_control = TaxReturnRpt.render_records(
            fileobj, y_control - 45, "purchase", company
        )
        y_control -= 20
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(30, y_control, "Net VAT due ")

        TaxReturnRpt.grand_totals["sales_grand_total"] = (
            TaxReturnRpt.totals["sales"]["vat_total"]
            + TaxReturnRpt.totals["sales"]["adj_total"]
        )
        TaxReturnRpt.grand_totals["purchase_grand_total"] = (
            TaxReturnRpt.totals["purchase"]["vat_total"]
            + TaxReturnRpt.totals["purchase"]["adj_total"]
        )
        TaxReturnRpt.grand_totals["net_total"] = (
            TaxReturnRpt.grand_totals["sales_grand_total"]
            - TaxReturnRpt.grand_totals["purchase_grand_total"]
        )

        fileobj.line(20, y_control - 20, 570, y_control - 20)

        header_sequence = [
            "Total value of due tax for the period ",
            "Total value of recoverable tax for the period",
            "Net VAT due(or reclaimed) for the period ",
        ]
        total_sequence = ["sales_grand_total", "purchase_grand_total", "net_total"]

        TaxReturnRpt.set_total_sequence(
            y_control - 40, header_sequence, total_sequence, fileobj
        )

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        PDF_FILE_NAME = "reports/tax_return.pdf"

        file_name = TaxReturnRpt.manage_pdf(
            RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, buffer)
        )

        return file_name
