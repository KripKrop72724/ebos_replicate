##for file handling
import io

import xlsxwriter

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import RPTHandler

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


class GLRBalance:

    # for managing accounts
    chart_accounts = []
    child_accounts = []

    totals = {"debit_total": 0, "credit_total": 0}

    # generation of report headers
    def set_csv_headers(workbook, worksheet, cell_ref):
        comp_format = workbook.add_format({"bold": True, "align": "left"})
        worksheet.write("D" + str(cell_ref), " # ", comp_format)
        worksheet.write("E" + str(cell_ref), "Voc # ", comp_format)
        worksheet.write("F" + str(cell_ref), "Date", comp_format)
        worksheet.write("G" + str(cell_ref), "Narration", comp_format)
        worksheet.write("H" + str(cell_ref), "Debit", comp_format)
        worksheet.write("I" + str(cell_ref), "Credit", comp_format)
        worksheet.write("J" + str(cell_ref), "Balance", comp_format)

    def handleNegative(canvas, x_control, y_control, value):
        value = str(value)
        if float(value) < 0:
            canvas.drawString(
                RPTHandler.calculate_small_x(x_control, value, 6),
                y_control,
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
            )
        else:
            canvas.drawString(
                RPTHandler.calculate_small_x(x_control, value, 6),
                y_control,
                "%.2f" % float(value),
            )

    def handleCsvNegative(worksheet, CELL_REF, ROW_REF, value, style):
        value = str(value)
        if float(value) < 0:
            worksheet.write(
                ROW_REF + str(CELL_REF),
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
                style,
            )
        else:
            worksheet.write(ROW_REF + str(CELL_REF), "%.2f" % float(value), style)

    def render_csv_vouchers(workbook, worksheet, balance, vouchers, cell_ref):
        cell_left_format = workbook.add_format({"align": "left"})
        cell_right_format = workbook.add_format({"align": "right"})
        for voucher in vouchers:
            worksheet.write(
                "D" + str(cell_ref),
                str(
                    RPTHandler.manageNestedValues(
                        voucher.vou_id.vou_type, "voucher_type"
                    )
                ),
                cell_left_format,
            )
            worksheet.write(
                "E" + str(cell_ref), str(voucher.vou_id.vou_num), cell_left_format
            )
            worksheet.write(
                "F" + str(cell_ref),
                str(RPTHandler.changeFormat(voucher.vou_id.vou_date)),
                cell_left_format,
            )
            worksheet.write(
                "G" + str(cell_ref), str(voucher.narration or ""), cell_left_format
            )
            balance = balance + voucher.bcurr_debit - voucher.bcurr_credit
            GLRBalance.handleCsvNegative(
                worksheet, cell_ref, "H", voucher.bcurr_debit, cell_right_format
            )
            GLRBalance.handleCsvNegative(
                worksheet, cell_ref, "I", voucher.bcurr_credit, cell_right_format
            )
            GLRBalance.handleCsvNegative(
                worksheet, cell_ref, "J", balance, cell_right_format
            )
            cell_ref += 1
        return cell_ref, balance    

    # for generating template of pdf
    def export_glr_pdf(
        company, account, subledger, from_date, to_date, op_bal, voc_rows, pdf_file_name
    ):
        from django.conf import settings
        from django.db.models import Sum
        from ebos2210.utils.u10_rpt_handler import GeneratePDF

        TEMPLATE_NAME = "ebos2210/reports/t10_gl_running_balance.html"
        PDF_FILE_NAME = pdf_file_name

        logo = (
            f"{settings.SITE_DOMAIN}{company.logo_file_link.url}"
            if company.logo_file_link
            else None
        )

        debit_total = voc_rows.aggregate(Sum("bcurr_debit"))['bcurr_debit__sum']
        credit_total = voc_rows.aggregate(Sum("bcurr_credit"))['bcurr_credit__sum']

        credit, debit = 0, 0        

        if op_bal > 0:
            debit = op_bal
        else:
            credit = op_bal
        
        cls_debit, cls_credit, balance = 0, 0, op_bal
        balance_list = []
        
        for voucher in voc_rows:
            balance = balance + voucher.bcurr_debit - voucher.bcurr_credit
            balance_list.append(balance)

        if balance < 0:
            cls_credit = balance
        else:
            cls_debit = balance

        params = {
            "company_logo": logo,
            "company": company,
            "account": account,
            "subledger": subledger,
            "from_date": from_date,
            "to_date": to_date,
            "debit": debit,
            "credit": credit,
            "vouchers": voc_rows,
            "balances": balance_list,
            "debit_total": debit_total,
            "credit_total": credit_total,
            "cls_debit": cls_debit,
            "cls_credit": cls_credit,
        }
        params.update({"title": "GL Transactions"}, **params)
        GLRBalance.chart_accounts.clear()

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)

    def export_glr_csv(account, subledger, from_date, to_date, op_bal, voc_rows):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        credit, debit = 0, 0

        # Add a bold format to use to highlight cells.
        title_format = workbook.add_format({"bold": True, "align": "left"})
        header_format = workbook.add_format({"bold": True, "align": "center"})
        value_format = workbook.add_format({"align": "left"})

        header_format.set_font_size(16)
        worksheet.merge_range("D4:J4", " GL Transactions ", header_format)

        CELL_REF = 6
        title_format.set_font_size(11)
        worksheet.set_column(3, CELL_REF, 15)
        worksheet.write("D" + str(CELL_REF), "Account # :", title_format)
        worksheet.write("D" + str(CELL_REF + 1), "A/C Name :", title_format)
        worksheet.write("D" + str(CELL_REF + 2), "Ledger A/C :", title_format)
        worksheet.write("H" + str(CELL_REF), "Period", title_format)
        worksheet.write("G" + str(CELL_REF + 3), "Opening Balance:", title_format)

        if op_bal > 0:
            debit = op_bal
        else:
            credit = op_bal

        value_format.set_font_size(11)
        worksheet.write(
            "E" + str(CELL_REF),
            RPTHandler.manageNestedValues(account, "account_num"),
            value_format,
        )
        worksheet.write(
            "E" + str(CELL_REF + 1),
            RPTHandler.manageNestedValues(account, "account_name"),
            value_format,
        )
        worksheet.write("E" + str(CELL_REF + 2), str(subledger), value_format)
        worksheet.write(
            "I" + str(CELL_REF),
            str(RPTHandler.changeFormat(from_date))
            + " to "
            + str(RPTHandler.changeFormat(to_date)),
            value_format,
        )
        worksheet.write("H" + str(CELL_REF + 3), "%.2f" % float(debit), value_format)
        worksheet.write("I" + str(CELL_REF + 3), "%.2f" % float(credit), value_format)

        CELL_REF += 5

        GLRBalance.set_csv_headers(workbook, worksheet, CELL_REF)
        CELL_REF += 1

        if len(voc_rows) > 0:

            CELL_REF, cls_bal = GLRBalance.render_csv_vouchers(
                workbook, worksheet, op_bal, voc_rows, CELL_REF
            )

            debit, credit = 0, 0
            if cls_bal < 0:
                credit = str(cls_bal).replace("-", "")
            else:
                debit = cls_bal

            worksheet.write("G" + str(CELL_REF + 3), "Closing Balance:", title_format)
            worksheet.write(
                "H" + str(CELL_REF + 3), "%.2f" % float(debit), value_format
            )
            worksheet.write(
                "I" + str(CELL_REF + 3), "%.2f" % float(credit), value_format
            )

        else:

            record_format = workbook.add_format({"bold": True, "align": "center"})
            record_format.set_font_size(13)
            worksheet.merge_range(
                "D" + str(CELL_REF + 1) + ":J" + str(CELL_REF + 1),
                " No record Found ",
                record_format,
            )

        workbook.close()
        buffer.seek(0)

        return buffer
