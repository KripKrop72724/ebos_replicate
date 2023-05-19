import io
import xlsxwriter

from django.conf import settings
from ebos2210.utils.u10_rpt_handler import GeneratePDF


class LedgerAccountSummary:

    def export_ldg_acc_pdf(company, date, subledger, accounts, debit_total, credit_total, pdf_file_name):
        TEMPLATE_NAME = "ebos2210/reports/t10_gl_ledger_summary.html"
        PDF_FILE_NAME = pdf_file_name

        logo = (
            f"{settings.SITE_DOMAIN}{company.logo_file_link.url}"
            if company.logo_file_link
            else None
        )

        cls_debit, cls_credit = 0, 0
        balance = float(debit_total or 0) - float(credit_total or 0)

        if balance < 0:
            cls_credit = balance
        else:
            cls_debit = balance

        params = {
            "company_logo": logo,
            "company": company,
            "subledger": subledger,
            "as_of": date,
            "accounts": accounts,
            "debit_total": debit_total,
            "credit_total": credit_total,
            "cls_debit": cls_debit,
            "cls_credit": cls_credit,
        }
        params.update({"title": "GL Account Summary"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)

    def export_ldg_acc_csv(date):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
