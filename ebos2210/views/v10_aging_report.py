##for file handling
import io
import sys

import xlsxwriter
from reportlab.lib.pagesizes import landscape, letter

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2210.utils.u10_rpt_handler import RPTHandler


class AgingReport:

    total = {"bucket1": 0, "bucket2": 0, "bucket3": 0, "bucket4": 0}
    bucket_index = ["bucket1", "bucket2", "bucket3", "bucket4"]

    # for maintaing negative values
    def handleCsvNegative(worksheet, CELL_REF, ROW_REF, value, style):
        value = str(value)
        if float(value) < 0:
            worksheet.write(
                ROW_REF + str(CELL_REF),
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
                style,
            )
        else:
            worksheet.write(ROW_REF + str(CELL_REF), "%.2f" % float(value), style)

    # generation of report headers
    def set_pdf_headers(canvas, y_axis, age1, age2, age3):
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(25, y_axis, "Inv. / Doc#")
        canvas.drawString(95, y_axis, "Due Dt.")
        canvas.drawString(145, y_axis, "Narration")
        canvas.drawString(460, y_axis, "0 - " + str(age1 - 1))
        canvas.drawString(555, y_axis, str(age1) + " - " + str(age2 - 1))
        canvas.drawString(635, y_axis, str(age2) + " - " + str(age3 - 1))
        canvas.drawString(715, y_axis, ">= " + str(age3))
        canvas.line(20, y_axis - 15, 770, y_axis - 15)

    # generation of report headers
    def set_csv_headers(workbook, worksheet, cell_ref, age1, age2, age3):
        comp_format = workbook.add_format({"bold": True, "align": "left"})
        worksheet.write("D" + str(cell_ref), "Inv. / Doc#", comp_format)
        worksheet.write("E" + str(cell_ref), "Due Dt.", comp_format)
        worksheet.write("F" + str(cell_ref), "Narration", comp_format)
        worksheet.write("G" + str(cell_ref), "0 - " + str(age1 - 1), comp_format)
        worksheet.write(
            "H" + str(cell_ref), str(age1) + " - " + str(age2 - 1), comp_format
        )
        worksheet.write(
            "I" + str(cell_ref), str(age2) + " - " + str(age3 - 1), comp_format
        )
        worksheet.write("J" + str(cell_ref), ">= " + str(age3), comp_format)

    def render_vouchers(canvas, vouchers, y_control, age1, age2, age3, run_date):
        canvas.setFont("Helvetica", 9)
        bucket = [
            range(0, age1),
            range(age1, age2),
            range(age2, age3),
            range(age3, sys.maxsize),
        ]
        if len(vouchers) > 0:
            for voucher in vouchers:
                x_index = 490
                canvas.drawString(
                    25,
                    y_control,
                    str(voucher.vou_line_ref or voucher.vou_id.vou_hdr_ref or "#"),
                )
                canvas.drawString(90, y_control, str(voucher.due_date or "--/--/----"))
                canvas.drawString(
                    145,
                    y_control,
                    str(voucher.narration or voucher.vou_id.comment1 or "----"),
                )
                if voucher.due_date == None or voucher.due_date == "":
                    diff_days = 0
                else:
                    diff_days = (run_date - voucher.due_date).days
                amount = (
                    voucher.bcurr_debit - voucher.bcurr_credit + voucher.alloc_amt_tot
                )
                buck_index = 0
                for buck in bucket:
                    if diff_days in buck:
                        RPTHandler.handleSmallNegative(
                            canvas, x_index, y_control, amount
                        )
                        AgingReport.total[
                            AgingReport.bucket_index[buck_index]
                        ] += amount
                    else:
                        canvas.drawString(
                            RPTHandler.calculate_small_x(x_index, "0.00", 5),
                            y_control,
                            "0.00",
                        )
                    x_index += 85
                    buck_index += 1
                y_control -= 20
                if y_control <= 20:
                    canvas.showPage()
                    y_control = 760
                    AgingReport.set_pdf_headers(canvas, 800, age1, age2, age3)
        else:
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(300, y_control, "No Record Found")
            y_control -= 20
        return y_control

    def render_csv_vouchers(
        workbook, worksheet, vouchers, cell_ref, age1, age2, age3, run_date
    ):
        cell_left_format = workbook.add_format({"align": "left"})
        cell_right_format = workbook.add_format({"align": "right"})
        bold_cell_center_format = workbook.add_format({"bold": True, "align": "center"})
        bucket = [
            range(0, age1),
            range(age1, age2),
            range(age2, age3),
            range(age3, sys.maxsize),
        ]
        cell_range = ["G", "H", "I", "J"]
        if len(vouchers) > 0:
            for voucher in vouchers:
                cat_index = 0
                worksheet.write(
                    "D" + str(cell_ref),
                    str(voucher.vou_line_ref or voucher.vou_id.vou_hdr_ref or "#"),
                    cell_left_format,
                )
                worksheet.write(
                    "E" + str(cell_ref),
                    str(voucher.due_date or "--/--/----"),
                    cell_left_format,
                )
                worksheet.write(
                    "F" + str(cell_ref),
                    str(voucher.narration or voucher.vou_id.comment1 or "----"),
                    cell_left_format,
                )
                if voucher.due_date == None or voucher.due_date == "":
                    diff_days = 0
                else:
                    diff_days = (run_date - voucher.due_date).days
                amount = (
                    voucher.bcurr_debit - voucher.bcurr_credit + voucher.alloc_amt_tot
                )
                buck_index = 0
                for buck in bucket:
                    if diff_days in buck:
                        AgingReport.handleCsvNegative(
                            worksheet,
                            cell_ref,
                            cell_range[cat_index],
                            amount,
                            cell_right_format,
                        )
                    else:
                        worksheet.write(
                            cell_range[cat_index] + str(cell_ref),
                            "0.00",
                            cell_right_format,
                        )
                    cat_index += 1
                    buck_index += 1
                cell_ref += 1
        else:
            worksheet.merge_range(
                "D" + str(cell_ref + 1) + ":J" + str(cell_ref + 1),
                "No Record Found",
                bold_cell_center_format,
            )
            cell_ref += 2
        return cell_ref

    # for generating template of pdf
    def export_agr_pdf(company, sublegder, date, age1, age2, age3, gl_vouchers):

        fields = T01Coa10._meta.fields
        for field in fields:
            print("fields is", str(field.attname))
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        AgingReport.total = {"bucket1": 0, "bucket2": 0, "bucket3": 0, "bucket4": 0}

        # Create the PDF object, using the buffer as its 'file.'
        fileobj = canvas.Canvas(buffer, pagesize=(landscape(letter)))

        RPTHandler.set_comp_header_landscape(True, company, fileobj)

        fileobj.setFont("Helvetica", 13)
        fileobj.drawString(310, 515, "Aging Report (Detailed)")
        fileobj.line(300, 505, 460, 505)

        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(640, 450, "Run Date:")

        fileobj.setFont("Helvetica", 10)
        sub_info = (
            str(RPTHandler.manageNestedValues(sublegder, "subledger_no"))
            + " - "
            + str(RPTHandler.manageNestedValues(sublegder, "subledger_name"))
        )
        fileobj.drawString(660, 470, "Consolidated")
        fileobj.drawString(30, 450, str(sub_info))
        fileobj.drawString(700, 450, str(RPTHandler.changeFormat(date)))

        fileobj.line(20, 435, 770, 435)

        AgingReport.set_pdf_headers(fileobj, 415, age1, age2, age3)

        y_control = AgingReport.render_vouchers(
            fileobj, gl_vouchers, 375, age1, age2, age3, date
        )

        x_index = 490
        grand_total = 0

        fileobj.setFont("Helvetica-Bold", 9)
        for bucket in AgingReport.bucket_index:
            RPTHandler.handleSmallNegative(
                fileobj, x_index, 70, AgingReport.total[bucket]
            )
            grand_total += AgingReport.total[bucket]
            x_index += 85

        fileobj.setFont("Helvetica-Bold", 11)
        fileobj.drawString(645, 20, "Total")
        fileobj.line(20, 40, 770, 40)

        fileobj.setFont("Helvetica", 9)
        RPTHandler.handleSmallNegative(fileobj, 745, 20, grand_total)

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return buffer

    def export_agr_csv(sublegder, date, age1, age2, age3, gl_vouchers):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        title_format = workbook.add_format({"bold": True, "align": "left"})
        header_format = workbook.add_format({"bold": True, "align": "center"})
        value_format = workbook.add_format({"align": "left"})

        header_format.set_font_size(16)
        worksheet.merge_range("D4:J4", "Aging Report (Detailed)", header_format)

        CELL_REF = 6

        title_format.set_font_size(11)
        worksheet.set_column(3, CELL_REF, 15)
        sub_info = (
            str(RPTHandler.manageNestedValues(sublegder, "subledger_no"))
            + " - "
            + str(RPTHandler.manageNestedValues(sublegder, "subledger_name"))
        )
        worksheet.write("D" + str(CELL_REF), sub_info, value_format)
        worksheet.write("H" + str(CELL_REF), "Run Date:", title_format)
        worksheet.write(
            "I" + str(CELL_REF), str(RPTHandler.changeFormat(date)), value_format
        )

        CELL_REF += 2

        AgingReport.set_csv_headers(workbook, worksheet, CELL_REF, age1, age2, age3)
        CELL_REF += 1

        AgingReport.render_csv_vouchers(
            workbook, worksheet, gl_vouchers, CELL_REF, age1, age2, age3, date
        )

        workbook.close()
        buffer.seek(0)

        return buffer
