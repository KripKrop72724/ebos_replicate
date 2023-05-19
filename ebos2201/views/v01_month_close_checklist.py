import io
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.utils.text import slugify
from reportlab.lib.colors import blue, magenta, pink
from reportlab.pdfgen import canvas

from ebos2201.utils import get_path


class MonthCloseCheckList:
    def __init__(self):
        self.year = 0
        self.period = 0
        self.months_in_year = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

    # generation of checklist headers
    def set_pdf_headers(self, fileobj, y_axis):
        fileobj.setFont("Helvetica-Bold", 12)
        fileobj.drawString(50, y_axis, f"Year: {self.year}")
        fileobj.drawString(
            420, y_axis, f"Month: {self.months_in_year[self.period - 1]}"
        )
        fileobj.line(20, y_axis - 15, 570, y_axis - 15)

    def render_check_list(self, fileobj, check_list, x_axis, y_axis):
        fileobj.setFont("Helvetica", 12)
        form = fileobj.acroForm

        for index, value in enumerate(check_list):
            form.checkbox(
                name=slugify(value),
                tooltip=value,
                x=x_axis - 25,
                y=(y_axis - 20 * index - 2),
                buttonStyle="check",
                borderColor=magenta,
                fillColor=pink,
                textColor=blue,
                forceBorder=True,
                size=12,
            )
            fileobj.drawString(x_axis, (y_axis - 20 * index), value)

    def pdf_file_handler(self, PDF_FILE_NAME, buffer):
        PDF_FILE_NAME = get_path(PDF_FILE_NAME)

        if default_storage.exists(PDF_FILE_NAME):
            default_storage.delete(PDF_FILE_NAME)

        file_name = default_storage.save(PDF_FILE_NAME, buffer)

        return file_name

    def manage_pdf(self, file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def print_pdf(self, obj):
        buffer = io.BytesIO()
        fileobj = canvas.Canvas(buffer)

        self.year = obj.year_num
        self.period = obj.period_num
        fileobj.setTitle("Month closing check list")
        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(190, 800, "Month Closing Check List")

        self.set_pdf_headers(fileobj, 760)
        check_list = [
            "Unposted entry check",
            "Pre-payment posting",
            "Intercompany / Division Account balance-distribution",
            "Depreciation posting",
            "PDC status update",
            "Bank Reconciliation",
            "Data integrity check (between modules)",
        ]
        self.render_check_list(fileobj, check_list, 210, 700)

        fileobj.showPage()

        fileobj.save()
        buffer.seek(0)

        PDF_FILE_NAME = "reports/month_closing_check_list.pdf"

        return self.manage_pdf(self.pdf_file_handler(PDF_FILE_NAME, buffer))
