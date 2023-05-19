import io
from datetime import date
from decimal import Decimal

import xlsxwriter
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from ebos2210.utils.u10_rpt_handler import RPTHandler

ASSET_STATUS = {"1": "Inventory", "2": "Scrap", "3": "Disposed"}


class DAReport:

    totals = {"initial": 0, "accum": 0, "disposable": 0, "salvage": 0}

    def set_pdf_headers(fileobj, y_control):
        fileobj.setFont("Helvetica-Bold", 9)
        fileobj.drawString(15, y_control, "Asset")
        fileobj.drawString(205, y_control, "Purchase Date")
        fileobj.drawString(300, y_control, "Initial Value")
        fileobj.drawString(380, y_control, "Life in Months")
        fileobj.drawString(480, y_control, "Accumulated")
        fileobj.drawString(480, y_control - 10, "Depreciation")
        fileobj.drawString(570, y_control, "Disposable")
        fileobj.drawString(580, y_control - 10, "Amount")
        fileobj.drawString(660, y_control, "Salvage")
        fileobj.drawString(660, y_control - 10, "Amount")
        fileobj.drawString(740, y_control, "Asset")
        fileobj.drawString(740, y_control - 10, "Status")

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
                                430, str(record.life_months or "0"), 5
                            ),
                            y_control,
                            str(record.life_months or "0"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                520, str(record.accum_dep or "0.00"), 5
                            ),
                            y_control,
                            str(record.accum_dep or "0.00"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                610, str(record.disposal_amt or "0.00"), 5
                            ),
                            y_control,
                            str(record.disposal_amt or "0.00"),
                        )
                        canvas.drawString(
                            RPTHandler.calculate_small_x(
                                700, str(record.salvage_amt or "0.00"), 5
                            ),
                            y_control,
                            str(record.salvage_amt or "0.00"),
                        )
                        canvas.drawString(
                            740, y_control, ASSET_STATUS[record.asset_status]
                        )
                        DAReport.totals["initial"] += Decimal(
                            str(record.asset_value or "0.00")
                        )
                        DAReport.totals["accum"] += Decimal(
                            str(record.accum_dep or "0.00")
                        )
                        DAReport.totals["disposable"] += Decimal(
                            str(record.disposal_amt or "0.00")
                        )
                        DAReport.totals["salvage"] += Decimal(
                            str(record.salvage_amt or "0.00")
                        )
                        y_control -= 20
                        if y_control <= 20:
                            canvas.showPage()
                            y_control = 570
                            DAReport.set_pdf_headers(canvas, 570)
                            canvas.line(10, 540, 780, 540)
        return y_control, count

    def export_dis_pdf(company, asset_records):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer, pagesize=(landscape(letter)))
        DAReport.totals = totals = {
            "initial": 0,
            "accum": 0,
            "disposable": 0,
            "salvage": 0,
        }

        RPTHandler.set_comp_header_landscape(True, company, fileobj)

        fileobj.setFont("Helvetica", 14)
        fileobj.drawString(300, 515, "Disposed Assets Report")
        fileobj.line(300, 510, 450, 510)

        fileobj.setFont("Helvetica", 9)
        current_date = date.today().strftime("%B %d, %Y")
        fileobj.drawString(340, 495, str(current_date))

        fileobj.line(10, 470, 780, 470)

        DAReport.set_pdf_headers(fileobj, 450)

        fileobj.line(10, 430, 780, 430)

        y_control, count = DAReport.render_records(fileobj, asset_records, 410, 0)

        if count == 0:
            fileobj.setFont("Helvetica-Bold", 10)
            fileobj.drawString(330, 410, "No Record Found")
        else:
            fileobj.line(10, y_control, 780, y_control)
            y_control -= 20
            fileobj.setFont("Helvetica-Bold", 10)
            fileobj.drawString(20, y_control, "Totals:")
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    325, str(DAReport.totals["initial"] or "0.00"), 5
                ),
                y_control,
                str(DAReport.totals["initial"] or "0.00"),
            )
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    520, str(DAReport.totals["accum"] or "0.00"), 5
                ),
                y_control,
                str(DAReport.totals["accum"] or "0.00"),
            )
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    610, str(DAReport.totals["disposable"] or "0.00"), 5
                ),
                y_control,
                str(DAReport.totals["disposable"] or "0.00"),
            )
            fileobj.drawString(
                RPTHandler.calculate_small_x(
                    700, str(DAReport.totals["salvage"] or "0.00"), 5
                ),
                y_control,
                str(DAReport.totals["salvage"] or "0.00"),
            )

        fileobj.showPage()
        fileobj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return buffer

    def export_dis_csv():
        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
