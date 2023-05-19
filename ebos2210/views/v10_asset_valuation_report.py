import io
from datetime import date
from decimal import Decimal

import xlsxwriter
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import RPTHandler


class AValuation:

    totals = {"initial": 0, "accum": 0, "current": 0}

    def set_pdf_headers(fileobj, y_control):
        fileobj.setFont("Helvetica-Bold", 9)
        fileobj.drawString(15, y_control, "Asset")
        fileobj.drawString(205, y_control, "Purchase Date")
        fileobj.drawString(290, y_control, "Initial Value")
        fileobj.drawString(360, y_control, "Life in Months")
        fileobj.drawString(450, y_control, "Depreciation")
        fileobj.drawString(455, y_control - 10, "Start Date")
        fileobj.drawString(550, y_control, "Depreciation")
        fileobj.drawString(560, y_control - 10, "Months")
        fileobj.drawString(640, y_control, "Accumulated")
        fileobj.drawString(640, y_control - 10, "Depreciation")
        fileobj.drawString(730, y_control, "Current")
        fileobj.drawString(730, y_control - 10, "Value")

    def render_records(canvas, asset_records, y_control, count):
        for asset_record in asset_records:
            if asset_record["records"].count() > 0:
                x_shift = 0
                canvas.setFont("Helvetica-Bold", 9.5)
                cat_value = RPTHandler.manageNestedValues(
                    asset_record["category"], "category_name"
                )
                if cat_value != "":
                    canvas.drawString(15, y_control, cat_value)
                    y_control -= 20
                    x_shift = 5
                for record in asset_record["records"]:
                    if RPTHandler.emptyValueHandler(record.asset_desc) != "":
                        count += 1
                        canvas.setFont("Helvetica", 8.5)
                        canvas.drawString(
                            15 + x_shift, y_control, str(record.asset_desc or "---")
                        )
                        canvas.drawString(
                            210 + x_shift,
                            y_control,
                            str(record.asset_pur_date or "---- / -- / --"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                325, str(record.asset_value or "0.00"), 5
                            ),
                            y_control,
                            str(record.asset_value or "0.00"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                410, str(record.life_months or "0"), 5
                            ),
                            y_control,
                            str(record.life_months or "0"),
                        )
                        canvas.drawString(
                            460, y_control, str(record.dep_start_dt or "---- / -- / --")
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                590, str(record.dep_months or "0"), 5
                            ),
                            y_control,
                            str(record.dep_months or "0"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                680, str(record.accum_dep or "0.00"), 5
                            ),
                            y_control,
                            str(record.accum_dep or "0.00"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                760, str(record.asset_status or "0.00"), 5
                            ),
                            y_control,
                            str(record.current_value or "0.00"),
                        )
                        AValuation.totals["initial"] += Decimal(
                            str(record.asset_value or "0.00")
                        )
                        AValuation.totals["accum"] += Decimal(
                            str(record.accum_dep or "0.00")
                        )
                        AValuation.totals["current"] += Decimal(
                            str(record.current_value or "0.00")
                        )
                        y_control -= 20
                        if y_control <= 20:
                            canvas.showPage()
                            y_control = 570
                            AValuation.set_pdf_headers(canvas, 570)
                            canvas.line(10, 540, 780, 540)
        return y_control, count

    def export_as_val_pdf(company, asset_records):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer, pagesize=(landscape(letter)))

        AValuation.totals = {"initial": 0, "accum": 0, "current": 0}

        RPTHandler.set_comp_header_landscape(True, company, fileobj)

        fileobj.setFont("Helvetica", 14)
        fileobj.drawString(310, 515, "Asset Valuation Report")
        fileobj.line(305, 510, 455, 510)

        fileobj.setFont("Helvetica", 9)
        current_date = date.today().strftime("%B %d, %Y")
        fileobj.drawString(350, 495, str(current_date))

        fileobj.line(10, 480, 780, 480)

        AValuation.set_pdf_headers(fileobj, 460)

        fileobj.line(10, 440, 780, 440)

        y_control, count = AValuation.render_records(fileobj, asset_records, 420, 0)

        if count == 0:
            fileobj.setFont("Helvetica-Bold", 10)
            fileobj.drawString(330, 420, "No Record Found")
        else:
            fileobj.line(10, y_control, 780, y_control)
            y_control -= 20
            fileobj.setFont("Helvetica-Bold", 10)
            fileobj.drawString(20, y_control, "Totals:")
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    325, str(AValuation.totals["initial"] or "0.00"), 5
                ),
                y_control,
                str(AValuation.totals["initial"] or "0.00"),
            )
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    680, str(AValuation.totals["accum"] or "0.00"), 5
                ),
                y_control,
                str(AValuation.totals["accum"] or "0.00"),
            )
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    760, str(AValuation.totals["current"] or "0.00"), 5
                ),
                y_control,
                str(AValuation.totals["current"] or "0.00"),
            )

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return buffer

    def export_as_val_csv():
        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
