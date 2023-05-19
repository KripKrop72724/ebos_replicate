##for file handling
import io
import xlsxwriter

from django.conf import settings
from ebos2210.utils.u10_rpt_handler import GeneratePDF


class SubledgerDetail:

    # for maintaining the margins in values
    def calculate_x(x_control, value):
        index = value.find(".")
        if index == -1:
            index = len(value)
        value = value[0:index]
        for val in range(1, len(value)):
            x_control -= 6
        return x_control

    def export_sub_pdf(**params):
        TEMPLATE_NAME = "ebos2210/reports/t10_gl_ledger_details.html"
        PDF_FILE_NAME = params['file_name']
        company = params["company"]

        logo = (
            f"{settings.SITE_DOMAIN}{company.logo_file_link.url}"
            if company.logo_file_link
            else None
        )

        params.update({
            "title": "Subledger Summary", 
            "sub_title": "Date Range",
            "company_logo": logo
            }, **params
        )

        return GeneratePDF.render(TEMPLATE_NAME, PDF_FILE_NAME, params)

    def export_sub_csv(from_date):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
