import io

import xlsxwriter
from reportlab.lib.pagesizes import landscape, letter

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import RPTHandler


class StmtAccount:

    # for managing accounts
    chart_accounts = []
    child_accounts = []

    totals = {
        "debit_total": 0,
        "credit_total": 0,
        "open_debit_total": 0,
        "open_credit_total": 0,
    }
    
    def handleNegative(canvas, x_control, y_control, value):
        value = str(value)
        if float(value) < 0:
            canvas.drawString(
                StmtAccount.calculate_x(x_control, value),
                y_control,
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
            )
        else:
            canvas.drawString(
                StmtAccount.calculate_x(x_control, value),
                y_control,
                "%.2f" % float(value),
            )

    # for maintaining the margins in values
    def calculate_x(x_control, value):
        index = value.find(".")
        if index == -1:
            index = len(value)
        value = value[0:index]
        for val in range(1, len(value)):
            x_control -= 4
        return x_control

    # for generating template of pdf   instance
    def export_soa_pdf(
        company, subledger, currency, rpt_type, from_date, to_date, op_bal, voc_rows, pdf_file_name
    ):
        from django.conf import settings
        from django.db.models import Sum
        from ebos2210.utils.u10_rpt_handler import GeneratePDF

        if rpt_type == "SAD":
            TEMPLATE_NAME = "ebos2210/reports/t10_gl_sad_balance.html"
        else:
            TEMPLATE_NAME = "ebos2210/reports/t10_gl_soa_balance.html"
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
        balance_list, open_amt_list, alloc_list = [], [], []
        
        for voucher in voc_rows:
            if rpt_type == "SAD":
                if voucher.bcurr_debit > 0:
                    open_amt = voucher.bcurr_debit + voucher.alloc_amt_tot
                else:
                    open_amt = voucher.bcurr_credit - voucher.alloc_amt_tot
                
                balance = balance + voucher.bcurr_debit - voucher.bcurr_credit
                balance_list.append(balance)
                open_amt_list.append(open_amt)
                if open_amt != 0 and open_amt != 0.00:
                    alloc_list.append(voucher.alloc_amt_tot)
                else:
                    alloc_list.append("0.00")
            else:
                open_debit = voucher.bcurr_debit + voucher.alloc_amt_tot
                open_credit = voucher.bcurr_credit - voucher.alloc_amt_tot
                balance = balance + open_debit - open_credit

        if balance < 0:
            cls_credit = balance
        else:
            cls_debit = balance

        params = {
            "company_logo": logo,
            "company": company,
            "subledger": subledger,
            "rpt_type": rpt_type,
            "currency": currency,
            "from_date": from_date,
            "to_date": to_date,
            "debit": debit,
            "credit": credit,
            "balances": balance_list,
            "open_amts": open_amt_list,
            "alloc_amts": alloc_list,
            "vouchers": voc_rows,
            "debit_total": debit_total,
            "credit_total": credit_total,
            "cls_debit": cls_debit,
            "cls_credit": cls_credit,
        }
        params.update({"title": "Statement of Account"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)
    
    def export_soa_csv(
        subledger, currency, rpt_type, from_date, to_date, op_bal, voc_rows
    ):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
