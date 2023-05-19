import io
import os
import textwrap
from decimal import Decimal

import pandas as pd
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from reportlab.pdfgen import canvas
from xlsxwriter.utility import xl_rowcol_to_cell

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2210.models.m10_fin_link import T10Gld11
from ebos2210.utils.u10_rpt_handler import RPTHandler
from ebos2201.utils import get_path


class GlAllocRpt:
    def __init__(self):
        self.company = None
        self.buffer = None
        self.fileobj = None
        self.yControl = 0
        self.totals = {"debit": 0, "credit": 0}

    # generation of report headers
    def set_pdf_headers(self, canvas, y_axis):
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(25, y_axis, "Voucher")
        canvas.drawString(30, y_axis - 15, "No")
        canvas.drawString(70, y_axis - 10, "Date")
        canvas.drawString(120, y_axis - 10, "Invoice")
        canvas.drawString(165, y_axis, "Cheque")
        canvas.drawString(172, y_axis - 15, "No.")
        canvas.drawString(220, y_axis, "Cheque")
        canvas.drawString(227, y_axis - 15, "Date")
        canvas.drawString(275, y_axis - 10, "Comments")
        canvas.drawString(470, y_axis - 10, "Debit")
        canvas.drawString(540, y_axis - 10, "Credit")
        canvas.line(20, y_axis - 20, 570, y_axis - 20)

    def render_details(self, trn_detail, gl_detail, type):
        self.fileobj.setFont("Helvetica", 8)
        if type == "credit":
            checkZero = (
                trn_detail.credit_alloc != 0
                and trn_detail.credit_alloc != 0.00
                and trn_detail.credit_alloc != None
            )
        else:
            checkZero = (
                trn_detail.debit_alloc != 0
                and trn_detail.debit_alloc != 0.00
                and trn_detail.debit_alloc != None
            )

        if checkZero:
            voc_num = (
                RPTHandler.manageNestedValues(gl_detail.vou_id.vou_type, "voucher_type")
                + " "
                + str(gl_detail.vou_id.vou_num)
            )
            self.fileobj.drawString(25, self.yControl, str(voc_num or "--"))
            self.fileobj.drawString(
                70,
                self.yControl,
                str(RPTHandler.manageNestedValues(gl_detail.vou_id, "vou_date") or ""),
            )
            if type == "debit":
                self.fileobj.drawString(
                    120,
                    self.yControl,
                    textwrap.shorten(
                        RPTHandler.emptyValueHandler(trn_detail.debit_ref),
                        width=10,
                        placeholder="...",
                    ),
                )
            else:
                self.fileobj.drawString(
                    120,
                    self.yControl,
                    textwrap.shorten(
                        RPTHandler.emptyValueHandler(trn_detail.credit_ref),
                        width=10,
                        placeholder="...",
                    ),
                )
            self.fileobj.drawString(
                165,
                self.yControl,
                textwrap.shorten(
                    RPTHandler.emptyValueHandler(gl_detail.chq_num),
                    width=12,
                    placeholder="...",
                ),
            )
            self.fileobj.drawString(225, self.yControl, str(gl_detail.chq_date or ""))
            comments = str(gl_detail.narration or "")
            if comments == "":
                comments = (
                    str(gl_detail.vou_id.comment1 or "")
                    + " "
                    + str(gl_detail.vou_id.comment2 or "")
                )
            self.fileobj.drawString(
                275,
                self.yControl,
                textwrap.shorten(
                    RPTHandler.emptyValueHandler(comments), width=40, placeholder="..."
                ),
            )
            if type == "debit":
                self.totals["debit"] += Decimal(trn_detail.debit_alloc or 0.00)
                self.fileobj.drawString(
                    RPTHandler.calculate_small_x(480, str(trn_detail.debit_alloc), 6),
                    self.yControl,
                    str(trn_detail.debit_alloc or "0.00"),
                )
                self.fileobj.drawString(550, self.yControl, "0.00")
            else:
                self.totals["credit"] += Decimal(trn_detail.credit_alloc or 0.00)
                self.fileobj.drawString(480, self.yControl, "0.00")
                self.fileobj.drawString(
                    RPTHandler.calculate_small_x(550, str(trn_detail.credit_alloc), 6),
                    self.yControl,
                    str(trn_detail.credit_alloc or "0.00"),
                )
            self.yControl -= 20
            if self.yControl <= 20:
                self.fileobj.showPage()
                self.yControl = 760
                self.set_pdf_headers(self.fileobj, 800)

    def changeFormat(self, date):
        day = date.day
        if day < 10:
            day = "0" + str(day)
        month = date.month
        if month < 10:
            month = "0" + str(month)
        year = date.year
        date_format = str(day) + " / " + str(month) + " / " + str(year)
        return date_format

    def manage_pdf(self, file_name):
        path = os.path.join(str(settings.MEDIA_ROOT), file_name)
        try:
            file_response = FileResponse(
                open(path, "rb"), content_type="application/pdf"
            )
            return file_response
        except FileNotFoundError:
            raise Http404()

    def init_pdf(self, obj):

        self.buffer = io.BytesIO()
        self.fileobj = canvas.Canvas(self.buffer)

        self.company = T01Div10.get_div_comp(obj.division)

        self.fileobj.setTitle("Allocation Report")

        RPTHandler.set_comp_header(True, self.company, self.fileobj)

        self.fileobj.setFont("Helvetica", 18)
        self.fileobj.drawString(230, 720, "Allocation Report")
        self.fileobj.line(225, 715, 370, 715)

        self.fileobj.setFont("Helvetica", 9)
        self.fileobj.drawString(30, 690, f"Allocation ID  : {obj.id}")
        self.fileobj.drawString(
            30, 670, f"Allocation Date  : {self.changeFormat(obj.vou_date)}"
        )
        self.fileobj.drawString(420, 690, f"Voucher No.  : {obj.vou_num}")
        self.fileobj.drawString(420, 670, f"Voucher Type  : {obj.vou_type}")

        self.fileobj.line(20, 650, 570, 650)
        self.set_pdf_headers(self.fileobj, 635)
        self.yControl = 600

    def print_pdf(self, obj):

        self.fileobj.line(450, self.yControl, 570, self.yControl)
        self.yControl -= 15
        self.fileobj.setFont("Helvetica-Bold", 9)
        self.fileobj.drawString(410, self.yControl, "Total")
        self.fileobj.setFont("Helvetica", 9)
        self.fileobj.drawString(
            RPTHandler.calculate_small_x(480, str(self.totals["debit"]), 6),
            self.yControl,
            str(self.totals["debit"] or "0.00"),
        )
        self.fileobj.drawString(
            RPTHandler.calculate_small_x(550, str(self.totals["credit"]), 6),
            self.yControl,
            str(self.totals["credit"] or "0.00"),
        )
        self.yControl -= 15
        self.fileobj.line(450, self.yControl, 570, self.yControl)

        self.fileobj.showPage()

        self.fileobj.save()
        self.buffer.seek(0)

        PDF_FILE_NAME = "reports/allocation_report.pdf"

        return self.manage_pdf(
            RPTHandler.print_pdf_file_handler(PDF_FILE_NAME, self.buffer)
        )


class GlAllocRptExl:
    def render_details(self, gl_alloc):

        data = {
            "Voucher No": [],
            "Date": [],
            "Invoice": [],
            "Cheque No.": [],
            "Comments": [],
            "Debit": [],
            "Credit": [],
        }

        # passing debit details
        for db_detail in gl_alloc.allocation_db.all():
            gl11_detail = T10Gld11.objects.get(id=db_detail.debit_id)

            if db_detail.debit_alloc not in [0, 0.00, None]:
                # Append voucher no
                voc_num = f"{RPTHandler.manageNestedValues(gl11_detail.vou_id.vou_type,'voucher_type')}/{gl11_detail.vou_id.vou_num}"
                data["Voucher No"].append(voc_num or "--")

                # Append voucher date
                data["Date"].append(
                    RPTHandler.manageNestedValues(gl11_detail.vou_id, "vou_date") or ""
                )

                # Append invoice
                data["Invoice"].append(
                    textwrap.shorten(
                        RPTHandler.emptyValueHandler(db_detail.debit_ref), width=10
                    )
                )

                # Append cheque no
                data["Cheque No."].append(
                    textwrap.shorten(
                        RPTHandler.emptyValueHandler(gl11_detail.chq_num), width=12
                    )
                )

                # Append comments
                data["Comments"].append(
                    textwrap.shorten((gl11_detail.narration or ""), width=40)
                )

                # Append debit
                data["Debit"].append(Decimal(db_detail.debit_alloc))

                # Append credit
                data["Credit"].append(Decimal("0.00"))

        # passing credit details
        for cr_detail in gl_alloc.allocation_cr.all():
            gl11_detail = T10Gld11.objects.get(id=cr_detail.credit_id)

            if cr_detail.credit_alloc not in [0, 0.00, None]:
                # Append voucher no
                voc_num = f"{RPTHandler.manageNestedValues(gl11_detail.vou_id.vou_type,'voucher_type')}/{gl11_detail.vou_id.vou_num}"
                data["Voucher No"].append(voc_num or "--")

                # Append voucher date
                data["Date"].append(
                    RPTHandler.manageNestedValues(gl11_detail.vou_id, "vou_date") or ""
                )

                # Append invoice
                data["Invoice"].append(
                    textwrap.shorten(
                        RPTHandler.emptyValueHandler(cr_detail.credit_ref), width=10
                    )
                )

                # Append cheque no
                data["Cheque No."].append(
                    textwrap.shorten(
                        RPTHandler.emptyValueHandler(gl11_detail.chq_num), width=12
                    )
                )

                # Append comments
                data["Comments"].append(
                    textwrap.shorten((gl11_detail.narration or ""), width=40)
                )

                # Append debit
                data["Debit"].append(Decimal("0.00"))

                # Append credit
                data["Credit"].append(Decimal(cr_detail.credit_alloc))

        return self.export_xl(data)

    def export_xl(self, data):
        mdf = pd.DataFrame(data)

        # We need the number of rows in order to place the totals
        number_rows = len(mdf.index)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        XL_FILE_NAME = get_path("reports/allocation_report.xlsx")

        file_path = os.path.join(str(settings.MEDIA_ROOT), XL_FILE_NAME)

        # Existing file remove
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
        mdf.to_excel(writer, index=False, sheet_name="allocation")

        # Get access to the workbook and sheet
        workbook = writer.book
        worksheet = writer.sheets["allocation"]

        # Reduce the zoom a little
        worksheet.set_zoom(100)
        textWrap = workbook.add_format({"text_wrap": "true"})
        header_format = workbook.add_format(
            {"bg_color": "yellow", "bold": True, "border": 1}
        )
        header_format.set_align("center")
        header_format.set_align("vcenter")
        worksheet.set_row(0, 30)

        # Write the column headers with the defined format.
        for col_num, value in enumerate(mdf.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Account info columns
        num_format = workbook.add_format({"align": "right"})
        worksheet.set_column("A:B", 12)
        worksheet.set_column("C:C", 10)
        worksheet.set_column("D:D", 15, num_format)
        worksheet.set_column("E:E", 50, textWrap)
        worksheet.set_column("F:G", 12, num_format)

        # Add total rows
        total_fmt = workbook.add_format(
            {
                "align": "right",
                "num_format": "#,##0.00",
                "bold": True,
                "size": 18,
                "border": 1,
            }
        )
        total_debit = sum(list(map(Decimal, data["Debit"])))
        total_credit = sum(list(map(Decimal, data["Credit"])))
        worksheet.write(xl_rowcol_to_cell(number_rows + 1, 5), total_debit, total_fmt)
        worksheet.write(xl_rowcol_to_cell(number_rows + 1, 6), total_credit, total_fmt)

        # Add a total label
        total_row_index = number_rows + 1
        total_str_fmt = workbook.add_format({"bold": True, "size": 18, "border": 1})
        worksheet.write_string(total_row_index, 4, "Total", total_str_fmt)
        worksheet.merge_range(
            f"A{total_row_index+1}:D{total_row_index+1}", "", textWrap
        )
        workbook.close()

        return XL_FILE_NAME
