##for file handling
import io

import xlsxwriter
from django.db.models import Q

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2201.models.m01_fin_mas import T01Coa10
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


class GLCBalance:

    totals = {"debit_total": 0, "credit_total": 0}

    # generation of report headers
    def set_pdf_headers(canvas, y_axis):
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(25, y_axis, "Voc Dt")
        canvas.drawString(100, y_axis, "Voc # ")
        canvas.drawString(80, y_axis - 15, "A/c Name")
        canvas.drawString(83, y_axis - 30, "Comment")
        canvas.drawString(170, y_axis - 10, "Ledger Name")
        canvas.drawString(350, y_axis, "Inv/Ref #")
        canvas.drawString(300, y_axis - 20, "Chq/Doc No")
        canvas.drawString(370, y_axis - 20, "Chq/Doc Dt")
        canvas.drawString(450, y_axis, "Debit")
        canvas.drawString(520, y_axis, "Credit")
        canvas.line(20, y_axis - 40, 570, y_axis - 40)

    def render_records(canvas, balance, vouchers, y_control):
        for voucher in vouchers:
            comment = (
                str(voucher.vou_id.comment1 or "")
                + " "
                + str(voucher.vou_id.comment2 or "")
            )
            canvas.setFont("Helvetica", 10)
            canvas.drawString(
                20, y_control, str(RPTHandler.changeFormat(voucher.vou_id.vou_date))
            )
            vou_rec = (
                RPTHandler.manageNestedValues(voucher.vou_id.vou_type, "voucher_type")
                + "  "
                + str(voucher.vou_id.vou_num)
            )
            canvas.drawString(90, y_control, vou_rec)
            canvas.drawString(90, y_control - 18, str(voucher.vou_coa))
            canvas.drawString(90, y_control - 36, str(voucher.narration or comment))
            canvas.drawString(160, y_control, str(voucher.vou_subledger))
            canvas.drawString(350, y_control, str(voucher.vou_line_ref))
            canvas.drawString(320, y_control - 20, str(voucher.chq_num))
            canvas.drawString(380, y_control - 20, str((voucher.chq_date)))
            GLCBalance.totals["debit_total"] += voucher.bcurr_debit
            GLCBalance.totals["credit_total"] += voucher.bcurr_credit
            balance = balance + voucher.bcurr_debit - voucher.bcurr_credit
            RPTHandler.handleSmallNegative(canvas, 470, y_control, voucher.bcurr_debit)
            RPTHandler.handleSmallNegative(canvas, 540, y_control, voucher.bcurr_credit)
            canvas.drawString(520, y_control, "")
            y_control -= 60
            if y_control <= 20:
                canvas.showPage()
                y_control = 750
                GLCBalance.set_pdf_headers(canvas, 810)
        return y_control, balance

    # for generating template of pdf
    def export_glc_pdf(
        company, account, subledger, from_date, to_date, op_bal, voc_rows, pdf_file_name
    ):
        from django.conf import settings
        from django.db.models import Sum
        from ebos2210.utils.u10_rpt_handler import GeneratePDF

        TEMPLATE_NAME = "ebos2210/reports/t10_gl_contra_balance.html"
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
        
        cls_debit, cls_credit, balance = 0, 0, 0
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
            "debit_total": debit_total,
            "credit_total": credit_total,
            "cls_debit": cls_debit,
            "cls_credit": cls_credit,
        }
        params.update({"title": "GL Transactions"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)

    def export_glc_csv(account, subledger, from_date, to_date, op_bal, voc_rows):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
