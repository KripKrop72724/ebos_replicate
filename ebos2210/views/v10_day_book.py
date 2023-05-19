import io

import xlsxwriter
from reportlab.lib.pagesizes import landscape, letter

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import RPTHandler


class DayOfBook:

    # for managing accounts
    chart_accounts = []

    totals = {
        "debit_total": 0,
        "credit_total": 0,
        "debit_grand_total": 0,
        "credit_grand_total": 0,
    }

    # file handling objects
    pdfBuffer = ""
    pdfFileObj = ""
    pdfYControl = 645
    last_voc_date = ""
    voucher_serial = 0

    # generation of report headers
    def set_pdf_headers(y_axis):
        stmt_type_x = [30, 70, 130, 220, 350, 420, 480, 530]
        DayOfBook.pdfFileObj.setFont("Helvetica-Bold", 8)
        DayOfBook.pdfFileObj.drawString(stmt_type_x[0], y_axis - 10, "SI. No.")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[1], y_axis, "Voucher Date")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[1] + 10, y_axis - 15, "A/C. #")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[2], y_axis, "Voucher Ref#.")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[2] + 30, y_axis - 15, "Sub Ledger")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[3], y_axis, "Remarks")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[3], y_axis - 15, "Narration")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[4], y_axis - 10, "Bill Ref.#")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[5], y_axis - 10, "Job")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[6], y_axis - 10, "Debit")
        DayOfBook.pdfFileObj.drawString(stmt_type_x[7], y_axis - 10, "Credit")
        DayOfBook.pdfFileObj.setFont("Helvetica", 8)
        DayOfBook.pdfFileObj.line(20, y_axis - 30, 570, y_axis - 30)

    # for maintaining the margins in values
    def calculate_x(x_control, value):
        index = value.find(".")
        if index == -1:
            index = len(value)
        value = value[0:index]
        for val in range(1, len(value)):
            x_control -= 4
        return x_control

    def initiationPDF(company, from_date, to_date):
        # Create a file-like buffer to receive PDF data.
        DayOfBook.pdfBuffer = io.BytesIO()

        DayOfBook.totals = {
            "debit_total": 0,
            "credit_total": 0,
            "debit_grand_total": 0,
            "credit_grand_total": 0,
        }

        DayOfBook.pdfFileObj = canvas.Canvas(DayOfBook.pdfBuffer)

        y_adjust = RPTHandler.set_comp_header(True, company, DayOfBook.pdfFileObj)

        DayOfBook.pdfFileObj.setFont("Helvetica", 16)
        DayOfBook.pdfFileObj.drawString(250, 730, " Day Book ")
        DayOfBook.pdfFileObj.line(245, 720, 335, 720)

        DayOfBook.pdfFileObj.setFont("Helvetica-Bold", 10)
        DayOfBook.pdfFileObj.drawString(375, 690, "From:")
        DayOfBook.pdfFileObj.drawString(490, 690, " to ")

        DayOfBook.pdfFileObj.setFont("Helvetica", 10)
        DayOfBook.pdfFileObj.drawString(
            430, 690, str(RPTHandler.changeFormat(from_date))
        )
        DayOfBook.pdfFileObj.drawString(510, 690, str(RPTHandler.changeFormat(to_date)))

        DayOfBook.pdfFileObj.line(20, 670, 570, 670)

        DayOfBook.set_pdf_headers(655)
        DayOfBook.pdfYControl = 610

    def render_totals():
        DayOfBook.pdfFileObj.line(
            400, DayOfBook.pdfYControl + 10, 570, DayOfBook.pdfYControl + 10
        )
        DayOfBook.pdfFileObj.drawString(410, DayOfBook.pdfYControl, "Total :")
        RPTHandler.handleSmallNegative(
            DayOfBook.pdfFileObj,
            490,
            DayOfBook.pdfYControl,
            DayOfBook.totals["debit_total"],
        )
        RPTHandler.handleSmallNegative(
            DayOfBook.pdfFileObj,
            540,
            DayOfBook.pdfYControl,
            DayOfBook.totals["credit_total"],
        )
        DayOfBook.pdfFileObj.line(
            20, DayOfBook.pdfYControl - 10, 570, DayOfBook.pdfYControl - 10
        )
        DayOfBook.pdfYControl -= 30
        DayOfBook.totals["debit_grand_total"] += DayOfBook.totals["debit_total"]
        DayOfBook.totals["credit_grand_total"] += DayOfBook.totals["credit_total"]
        DayOfBook.totals["debit_total"], DayOfBook.totals["credit_total"] = 0, 0

    def set_next_page():
        DayOfBook.pdfFileObj.showPage()
        DayOfBook.pdfYControl = 760
        DayOfBook.set_pdf_headers(800)

    def render_vouchers(voucher, voc_rows, count):
        DayOfBook.pdfFileObj.setFont("Helvetica-Bold", 8)
        if DayOfBook.last_voc_date != str(voucher.vou_date):
            DayOfBook.last_voc_date = str(voucher.vou_date)
            DayOfBook.voucher_serial += 1
            if count != 0:
                DayOfBook.render_totals()
            DayOfBook.pdfFileObj.drawString(
                40, DayOfBook.pdfYControl, str(DayOfBook.voucher_serial)
            )
            DayOfBook.pdfFileObj.drawString(
                70,
                DayOfBook.pdfYControl,
                str(RPTHandler.changeFormat(voucher.vou_date)),
            )
        else:
            DayOfBook.pdfYControl += 10
        DayOfBook.pdfFileObj.drawString(
            130,
            DayOfBook.pdfYControl - 20,
            str(RPTHandler.manageNestedValues(voucher.vou_type, "voucher_type")),
        )
        DayOfBook.pdfFileObj.drawString(
            145, DayOfBook.pdfYControl - 20, str(voucher.vou_num)
        )
        DayOfBook.pdfFileObj.drawString(
            170, DayOfBook.pdfYControl - 20, str(voucher.subledger)
        )
        comment = str(voucher.comment1)  # + ' ' + str(voucher.comment2)
        DayOfBook.pdfFileObj.setFont("Helvetica", 8)
        DayOfBook.pdfFileObj.drawString(240, DayOfBook.pdfYControl - 20, comment)
        for row in voc_rows:
            DayOfBook.pdfYControl -= 20
            if DayOfBook.pdfYControl <= 20:
                DayOfBook.set_next_page()
            row_info = (
                "("
                + str(RPTHandler.manageNestedValues(row.vou_coa, "account_num"))
                + ") "
                + str(RPTHandler.manageNestedValues(row.vou_coa, "account_name"))
            )
            DayOfBook.pdfFileObj.drawString(60, DayOfBook.pdfYControl - 20, row_info)
            DayOfBook.pdfFileObj.drawString(
                220, DayOfBook.pdfYControl - 20, str(row.narration)
            )
            DayOfBook.totals["debit_total"] += float(row.bcurr_debit)
            DayOfBook.totals["credit_total"] += float(row.bcurr_credit)
            RPTHandler.handleSmallNegative(
                DayOfBook.pdfFileObj, 490, DayOfBook.pdfYControl - 20, row.bcurr_debit
            )
            RPTHandler.handleSmallNegative(
                DayOfBook.pdfFileObj, 540, DayOfBook.pdfYControl - 20, row.bcurr_credit
            )
        DayOfBook.pdfYControl -= 50
        if DayOfBook.pdfYControl <= 50:
            DayOfBook.set_next_page()

    # for generating template of pdf   instance
    def export_dbk_pdf(company, from_date, to_date, op_bal, vouchers):

        DayOfBook.pdfFileObj.setFont("Helvetica-Bold", 8)
        DayOfBook.render_totals()  # to show totals for last record
        DayOfBook.pdfFileObj.drawString(380, DayOfBook.pdfYControl, "Grand Total :")
        RPTHandler.handleSmallNegative(
            DayOfBook.pdfFileObj,
            490,
            DayOfBook.pdfYControl,
            DayOfBook.totals["debit_grand_total"],
        )
        RPTHandler.handleSmallNegative(
            DayOfBook.pdfFileObj,
            540,
            DayOfBook.pdfYControl,
            DayOfBook.totals["credit_grand_total"],
        )
        DayOfBook.pdfFileObj.showPage()
        DayOfBook.pdfFileObj.save()

        DayOfBook.chart_accounts.clear()
        DayOfBook.voucher_serial = 0
        DayOfBook.last_voc_date = ""

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        DayOfBook.pdfBuffer.seek(0)
        return DayOfBook.pdfBuffer

    def export_dbk_csv(from_date, to_date, op_bal, vouchers):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        DayOfBook.pdfBuffer.seek(0)

        return DayOfBook.pdfBuffer
