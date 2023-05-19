import io
import xlsxwriter

from django.conf import settings
from ebos2210.utils.u10_rpt_handler import GeneratePDF


class ChartAccountSummary:

    def export_chr_acc_pdf(rpt_code, company, date, coa, subledgers, debit_total, credit_total, pdf_file_name):
        TEMPLATE_NAME = "ebos2210/reports/t10_coa_acc_summary.html"
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
            "rpt_code": rpt_code,
            "coa": coa,
            "as_of": date,
            "subledgers": subledgers,
            "debit_total": debit_total,
            "credit_total": credit_total,
            "cls_debit": cls_debit,
            "cls_credit": cls_credit,
        }

        if rpt_code == "SLC":
            params.update({
                    "title": "Subledger Summary",
                    "sub_title": "As Of Date"
                    }, 
                    **params
                )
        else:
            params.update({"title": "Chart Account Summary"}, **params)

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)

    def export_chr_acc_csv(date):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
