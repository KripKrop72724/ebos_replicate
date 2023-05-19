from datetime import datetime, timedelta
from io import BytesIO

from django.core.files.storage import default_storage
from django.template.loader import get_template
from xhtml2pdf import pisa

from ebos2201.utils import get_path

EMP_HANDLERS = ["", "NULL", None]


class RPTHandler:

    # for maintaining the margins in values
    def calculate_x(x_control, value):
        value = str(value)
        index = value.find(".")
        if index == -1:
            index = len(value)
        value = value[0:index]
        for val in range(1, len(value)):
            x_control -= 7
        return x_control

    # for maintaining the margins in values
    def calculate_small_x(x_control, value, margin):
        index = value.find(".")
        if index == -1:
            index = len(value)
        value = value[0:index]
        for val in range(1, len(value)):
            x_control -= margin
        return x_control

    # for maintaing negative values
    def handleSmallNegative(canvas, x_control, y_control, value):
        value = str(value)
        if float(value) < 0:
            canvas.drawString(
                RPTHandler.calculate_small_x(x_control, value, 5),
                y_control,
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
            )
        else:
            canvas.drawString(
                RPTHandler.calculate_small_x(x_control, value, 5),
                y_control,
                "%.2f" % float(value),
            )

    # for maintaining empty values
    def emptyValueHandler(value):
        if value in EMP_HANDLERS:
            return ""
        else:
            return str(value)

    def manageNestedValues(parent, child):
        if parent in EMP_HANDLERS:
            return ""
        else:
            parent = parent.__dict__
            return parent[child]

    def changeFormat(date):
        day = date.day if date else 0
        if day < 10:
            day = "0" + str(day)

        month = date.month if date else 0
        if month < 10:
            month = "0" + str(month)

        year = date.year if date else 0
        date_format = str(day) + "/" + str(month) + "/" + str(year)

        return date_format

    def check_if_last_day_of_month(to_date):
        delta = timedelta(days=1)
        next_day = to_date + delta
        if to_date.month != next_day.month:
            return True
        return False

    def set_comp_header(print_option, company, pdfFileObj):

        y_adjust = 0

        if print_option == True:

            pdfFileObj.setFont("Helvetica", 9)
            pdfFileObj.drawString(430, 815, f"{datetime.now()}")

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

    # to adjust company header in landscape mode
    def set_comp_header_landscape(print_option, company, fileobj):

        y_adjust = 0

        if print_option == True:

            fileobj.setFont("Helvetica", 18)
            fileobj.drawString(25, 580, company.company_name)
            fileobj.setFont("Helvetica", 12)
            fileobj.drawString(25, 560, company.company_address)
            fileobj.drawString(25, 545, company.company_location)

            # display logo if any logo is uploaded for company
            if (
                str(company.logo_file_link) != ""
                and str(company.logo_file_link) != None
            ):
                logo_path = "documents/" + str(company.logo_file_link)
                fileobj.drawInlineImage(logo_path, 700, 550, 50, 45)

            y_adjust = 90

        return y_adjust

    def print_pdf_file_handler(PDF_FILE_NAME, buffer):
        PDF_FILE_NAME = get_path(PDF_FILE_NAME)

        if default_storage.exists(PDF_FILE_NAME):
            default_storage.delete(PDF_FILE_NAME)

        file_name = default_storage.save(PDF_FILE_NAME, buffer)

        return file_name


class GeneratePDF:
    @staticmethod
    def render(src_path: str, dst_path: str, params: dict) -> str:

        template = get_template(src_path)
        html = template.render(params)

        dst_path = get_path(dst_path)
        
        if default_storage.exists(dst_path):
            default_storage.delete(dst_path)

        response = default_storage.open(dst_path, "wb")
        pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        response.close()

        return dst_path
