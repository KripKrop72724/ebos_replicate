##for file handling
import io
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404

##for pdf file generation
from reportlab.pdfgen import canvas
from ebos2201.utils import get_path

from ebos2201.models.m01_fin_mas import T01Coa10

ACCTYPE_CHOICE = {
    "0": "----",
    "1": "GL",
    "2": "Bank",
    "3": "Cash",
    "4": "COGS",
    "5": "Equity",
}
COASLCAT_CHOICE = {
    "0": "----",
    "1": "Receivable",
    "2": "Payable",
    "3": "Fixed Asset",
    "4": "Entity",
}

EMP_HANDLERS = ["", "NULL", None]


class COAMaster:

    chart_accounts = []
    company = ""

    def get_all_accounts(division):
        COAMaster.company = division.company
        acc_1s = T01Coa10.objects.filter(
            parent=None, division__division_name=division
        ).order_by("account_group")
        COAMaster.pre_transversal(acc_1s, division)

        return COAMaster.chart_accounts

    def pre_transversal(accounts, division):
        for acc in accounts:
            COAMaster.chart_accounts.append(acc)
            acc_list = T01Coa10.objects.filter(
                parent=acc.id, division__division_name=division
            )
            COAMaster.pre_transversal(acc_list, division)

    def manageNestedValues(parent, child):
        if parent in EMP_HANDLERS:
            return ""
        else:
            parent = parent.__dict__
            return str(parent[child])

    def set_comp_header(print_option, company, pdfFileObj):

        y_adjust = 0

        if print_option == True:

            pdfFileObj.setFont("Helvetica", 18)
            pdfFileObj.drawString(25, 800, company.company_name)
            pdfFileObj.setFont("Helvetica", 12)
            pdfFileObj.drawString(25, 775, company.company_address)
            pdfFileObj.drawString(25, 760, company.company_location)

            # display logo if any logo is uploaded for company
            if (
                str(company.logo_file_link) != ""
                and str(company.logo_file_link) != None
            ):
                logo_path = "documents/" + str(company.logo_file_link)
                pdfFileObj.drawInlineImage(logo_path, 500, 770, 50, 45)

            y_adjust = 90

        return y_adjust

    def print_pdf_file_handler(PDF_FILE_NAME, buffer):
        PDF_FILE_NAME = get_path(PDF_FILE_NAME)

        if default_storage.exists(PDF_FILE_NAME):
            default_storage.delete(PDF_FILE_NAME)

        file_name = default_storage.save(PDF_FILE_NAME, buffer)

        return file_name

    # generation of report headers
    def set_pdf_headers(fileobj, y_axis):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(30, y_axis, "A/c #")
        fileobj.drawString(70, y_axis, "Account Name")
        fileobj.drawString(280, y_axis, "A/c Type")
        fileobj.drawString(340, y_axis, "SL Cat")
        fileobj.drawString(395, y_axis, "SL Type")
        fileobj.drawString(450, y_axis, "Activity")
        fileobj.drawString(500, y_axis, "Cashflow Type")
        fileobj.line(20, y_axis - 10, 575, y_axis - 10)

    def checkForNull(value):
        if value in EMP_HANDLERS:
            return "0"
        else:
            return value

    def checkNestedNull(value):
        if value in EMP_HANDLERS:
            return "----"
        else:
            return value

    def render_accounts(canvas, accounts, y_control):
        for account in accounts:
            x_shift = 70
            canvas.setFont("Helvetica", 9)
            for val in range(0, account.level):
                x_shift += 10
            canvas.drawString(30, y_control, account.account_num)
            canvas.drawString(x_shift, y_control, account.account_name)
            canvas.drawString(
                280,
                y_control,
                ACCTYPE_CHOICE[COAMaster.checkForNull(account.account_type)],
            )
            canvas.drawString(
                340,
                y_control,
                COASLCAT_CHOICE[COAMaster.checkForNull(account.coa_sl_cat)],
            )
            canvas.drawString(
                395,
                y_control,
                COAMaster.checkNestedNull(
                    COAMaster.manageNestedValues(account.coa_sl_type, "sl_type_code")
                ),
            )
            canvas.drawString(
                460,
                y_control,
                COAMaster.checkNestedNull(
                    COAMaster.manageNestedValues(account.activity_group, "activity_cat")
                ),
            )
            canvas.drawString(
                530,
                y_control,
                COAMaster.checkNestedNull(
                    COAMaster.manageNestedValues(account.cashflow_group, "cashflow_cat")
                ),
            )

            y_control -= 20
            if y_control <= 20:
                canvas.showPage()
                y_control = 760
                COAMaster.set_pdf_headers(canvas, 800)

    def manage_pdf(file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def init_pdf(division):

        buffer = io.BytesIO()

        fileobj = canvas.Canvas(buffer)

        COAMaster.set_comp_header(True, COAMaster.company, fileobj)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(190, 730, "Chart of Accounts Master")
        # fileobj.line(190,720,390,720)

        fileobj.setFont("Helvetica", 12)
        fileobj.drawString(190, 710, "( " + str(division) + " )")

        fileobj.line(20, 690, 575, 690)
        COAMaster.set_pdf_headers(fileobj, 670)

        COAMaster.render_accounts(fileobj, COAMaster.chart_accounts, 640)

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        # clearing out the global data holders

        COAMaster.chart_accounts.clear()
        COAMaster.company = ""

        PDF_FILE_NAME = "reports/coa_master_" + str(division.id) + ".pdf"

        return COAMaster.manage_pdf(
            COAMaster.print_pdf_file_handler(PDF_FILE_NAME, buffer)
        )
