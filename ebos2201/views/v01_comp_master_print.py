##for file handling
import io
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404

##for pdf file generation
from reportlab.pdfgen import canvas
from ebos2201.utils import get_path

from ebos2201.models.m01_core_mas import T01Com10, T01Div10

ACCTYPE_CHOICE = {
    "0": "-----",
    "1": "GL",
    "2": "Bank",
    "3": "Cash",
    "4": "COGS",
    "5": "Equity",
}
ACCGRP_CHOICE = {
    "0": "-----",
    "1": "Asset",
    "2": "Liability",
    "3": "Income",
    "4": "Expense",
}
COACTL_CHOICE = {"0": "-----", "1": "Rollup", "2": "Postable"}
COASLCAT_CHOICE = {
    "0": "-----",
    "1": "Receivable",
    "2": "Payable",
    "3": "Fixed Asset",
    "4": "Entity",
}

EMP_HANDLERS = ["", "NULL", None]


class COMPMaster:

    companies = []

    def get_all_comps():
        acc_1s = T01Com10.objects.filter(parent=None)
        COMPMaster.pre_transversal(acc_1s)

        return COMPMaster.companies

    def pre_transversal(accounts):
        for acc in accounts:
            COMPMaster.companies.append(acc)
            acc_list = T01Com10.objects.filter(parent=acc.id)
            COMPMaster.pre_transversal(acc_list)

    def get_divisions(company):
        divisions = []
        for div in T01Div10.objects.filter(company__id=company.id):
            divisions.append(div)
        return divisions

    def print_pdf_file_handler(PDF_FILE_NAME, buffer):
        PDF_FILE_NAME = get_path(PDF_FILE_NAME)

        if default_storage.exists(PDF_FILE_NAME):
            default_storage.delete(PDF_FILE_NAME)

        file_name = default_storage.save(PDF_FILE_NAME, buffer)

        return file_name

    # generation of report headers
    def set_pdf_headers(fileobj, y_axis):
        fileobj.setFont("Helvetica-Bold", 10)
        fileobj.drawString(30, y_axis, "Co #")
        fileobj.drawString(60, y_axis, "Name/Title")
        fileobj.drawString(280, y_axis, "Address")
        fileobj.drawString(400, y_axis, "Location")
        fileobj.drawString(520, y_axis, "Logo")
        fileobj.line(20, y_axis - 20, 570, y_axis - 20)

    def checkForNull(value):
        if value in EMP_HANDLERS:
            return "----"
        else:
            return value

    def render_companies(canvas, companies, y_control):
        for comp in companies:
            x_shift = 60
            canvas.setFont("Helvetica", 10)
            for val in range(0, comp.level):
                x_shift += 10
            canvas.drawString(30, y_control, str(comp.id))
            canvas.drawString(x_shift, y_control, comp.company_name)
            canvas.drawString(
                280, y_control, COMPMaster.checkForNull(comp.company_address)
            )
            canvas.drawString(
                400, y_control, COMPMaster.checkForNull(comp.company_location)
            )
            # display logo if any logo is uploaded for company
            if str(comp.logo_file_link) != "" and str(comp.logo_file_link) != None:
                logo_path = "documents/" + str(comp.logo_file_link)
                canvas.drawInlineImage(logo_path, 530, y_control - 2, 15, 15)
            y_control -= 20
            y_control = COMPMaster.render_division(
                canvas, x_shift + 15, y_control, COMPMaster.get_divisions(comp)
            )
            if y_control <= 20:
                canvas.showPage()
                y_control = 760
                COMPMaster.set_pdf_headers(canvas, 800)

    def render_division(canvas, x_shift, y_control, divisions):
        if len(divisions) > 0:
            canvas.setFont("Helvetica", 10)
            for divi in divisions:
                canvas.setFillColor("brown")
                canvas.drawString(x_shift, y_control, divi.division_name)
                canvas.drawString(280, y_control, divi.division_addr)
                canvas.drawString(400, y_control, divi.division_location)
                y_control -= 20

        canvas.setFillColor("black")

        return y_control

    def manage_pdf(file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def init_pdf():

        buffer = io.BytesIO()

        fileobj = canvas.Canvas(buffer)

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(220, 800, "Company Master")
        # fileobj.line(190,720,390,720)

        fileobj.line(20, 780, 570, 780)
        COMPMaster.set_pdf_headers(fileobj, 760)

        COMPMaster.render_companies(fileobj, COMPMaster.companies, 720)

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)

        # clearing out the global data holders

        COMPMaster.companies.clear()

        PDF_FILE_NAME = "reports/comp_master.pdf"

        return COMPMaster.manage_pdf(
            COMPMaster.print_pdf_file_handler(PDF_FILE_NAME, buffer)
        )
