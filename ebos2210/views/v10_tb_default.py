##for file handling
import io

import xlsxwriter
from django.conf import settings

##for pdf file generation
from reportlab.pdfgen import canvas

from ebos2201.models.m01_fin_mas import T01Coa10
from ebos2210.utils.u10_rpt_handler import RPTHandler

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


class TBDefault:

    # for managing accounts
    chart_accounts = []
    child_accounts = []

    totals = {}

    def get_all_accounts(division):
        acc_1s = T01Coa10.objects.filter(
            parent=None, division__division_name=division
        ).order_by("account_group")
        TBDefault.pre_transversal(acc_1s, division)
        return TBDefault.chart_accounts

    def pre_transversal(accounts, division):
        for acc in accounts:
            TBDefault.chart_accounts.append(acc)
            acc_list = T01Coa10.objects.filter(
                parent=acc.id, division__division_name=division
            )
            TBDefault.pre_transversal(acc_list, division)

    def fetch_children(accounts, division):
        for acc in accounts:
            TBDefault.child_accounts.append(acc)
            acc_list = T01Coa10.objects.filter(
                parent=acc.id, division__division_name=division
            )
            TBDefault.fetch_children(acc_list, division)

    # for generating title for the report
    def fetchTitle(tb_type=None, year=None, month=None, as_of_date=None):
        if as_of_date:
            report_title = f"Trial Balance as of {as_of_date.strftime(settings.DATE_INPUT_FORMATS[0])}"
        else:
            if tb_type == "1":
                report_title = "Annual Opening Trial Balance as of "
            elif tb_type == "2":
                report_title = "Annual Closing Trial Balance as of "
            elif tb_type == "3":
                report_title = "Trial Balance as of "

            if month:
                if month in range(13, 19):
                    if month == 13:
                        report_title += (
                            f"{MONTH_NAMES[int(1)-1]} to {MONTH_NAMES[int(3)-1]}"
                        )
                    elif month == 14:
                        report_title += (
                            f"{MONTH_NAMES[int(4)-1]} to {MONTH_NAMES[int(6)-1]}"
                        )
                    elif month == 15:
                        report_title += (
                            f"{MONTH_NAMES[int(7)-1]} to {MONTH_NAMES[int(9)-1]}"
                        )
                    elif month == 16:
                        report_title += (
                            f"{MONTH_NAMES[int(10)-1]} to {MONTH_NAMES[int(12)-1]}"
                        )
                    elif month == 17:
                        report_title += (
                            f"{MONTH_NAMES[int(1)-1]} to {MONTH_NAMES[int(6)-1]}"
                        )
                    else:
                        report_title += (
                            f"{MONTH_NAMES[int(7)-1]} to {MONTH_NAMES[int(12)-1]}"
                        )
                else:
                    report_title += MONTH_NAMES[int(month) - 1]

            report_title += f" {str(year)}"

        return report_title

    # generation of report headers
    def set_pdf_headers(canvas, y_axis):
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(30, y_axis, "A/c #")
        canvas.drawString(95, y_axis, "Account Name")
        canvas.drawString(390, y_axis, "Debit")
        canvas.drawString(500, y_axis, "Credit")
        canvas.line(20, y_axis - 15, 570, y_axis - 15)

    def render_accounts(canvas, accounts, y_control, debits, credits, zero_value):
        for account in accounts:
            if zero_value and debits[account.id] == "0" and credits[account.id] == "0":
                continue
            else:
                x_shift = 95
                canvas.setFont("Helvetica", 11)
                for val in range(0, account.level):
                    x_shift += 10
                canvas.drawString(30, y_control, account.account_num)
                canvas.drawString(x_shift, y_control, account.account_name)
                credit_amount = str(credits[account.id]).replace("-", "")
                # showing rollsups in bold
                if account.coa_control == "1":
                    canvas.setFont("Helvetica-Bold", 11)
                else:
                    TBDefault.totals["debit"] += float(debits[account.id])
                    TBDefault.totals["credit"] += float(credit_amount)

                canvas.drawString(
                    RPTHandler.calculate_x(400, debits[account.id]),
                    y_control,
                    "%.2f" % float(debits[account.id]),
                )
                canvas.drawString(
                    RPTHandler.calculate_x(510, credit_amount),
                    y_control,
                    "%.2f" % float(credit_amount),
                )
                y_control -= 20
                if y_control <= 20:
                    canvas.showPage()
                    y_control = 760
                    TBDefault.set_pdf_headers(canvas, 800)
        return y_control

    def render_csv_accounts(workbook, worksheet, accounts, cell_ref, debits, credits, zero_value):
        cell_left_format = workbook.add_format({"align": "left"})
        cell_right_format = workbook.add_format({"align": "right"})
        bold_cell_right_format = workbook.add_format({"bold": True, "align": "right"})
        for account in accounts:            
            if zero_value and debits[account.id] == "0" and credits[account.id] == "0":
                continue
            else:
                worksheet.write("D" + str(cell_ref), account.account_num, cell_left_format)
                width = len(account.account_name) + 15
                worksheet.set_column(4, cell_ref, width)
                worksheet.write("E" + str(cell_ref), account.account_name, cell_left_format)
                credit_amount = str(credits[account.id]).replace("-", "")
                # showing rollsups in bold
                if account.coa_control == "1":
                    worksheet.write(
                        "F" + str(cell_ref),
                        "%.2f" % float(debits[account.id]),
                        bold_cell_right_format,
                    )
                    worksheet.write(
                        "G" + str(cell_ref),
                        "%.2f" % float(credit_amount),
                        bold_cell_right_format,
                    )
                else:
                    worksheet.write(
                        "F" + str(cell_ref),
                        "%.2f" % float(debits[account.id]),
                        cell_right_format,
                    )
                    worksheet.write(
                        "G" + str(cell_ref),
                        "%.2f" % float(credit_amount),
                        cell_right_format,
                    )
                cell_ref += 1
        return cell_ref

    # for generating template of pdf
    def export_tb_pdf(
        company,
        tb_type=None,
        year=None,
        month=None,
        debits=None,
        credits=None,
        as_of_date=None,
        zero_value=None
    ):

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        TBDefault.totals = {"debit": 0, "credit": 0}

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        RPTHandler.set_comp_header(True, company, fileobj)

        report_title = TBDefault.fetchTitle(
            tb_type=tb_type, year=year, month=month, as_of_date=as_of_date
        )

        fileobj.setFont("Helvetica", 17)
        fileobj.drawString(150, 730, report_title)
        fileobj.line(20, 715, 570, 715)

        TBDefault.set_pdf_headers(fileobj, 690)

        if len(TBDefault.chart_accounts) > 0:
            y_control = TBDefault.render_accounts(
                fileobj, TBDefault.chart_accounts, 650, debits, credits, zero_value
            )

            fileobj.line(20, y_control, 570, y_control)
            y_control -= 20
            total_debit = "%.2f" % float(TBDefault.totals["debit"])
            total_credit = "%.2f" % float(TBDefault.totals["credit"])
            
            fileobj.drawString(
                RPTHandler.calculate_x(400, str(TBDefault.totals["debit"])),
                y_control,
                total_debit,
            )
            fileobj.drawString(
                RPTHandler.calculate_x(510, str(TBDefault.totals["credit"])),
                y_control,
                total_credit,
            )

            difference = float(total_debit) - float(total_credit)
            
            if difference != 0:
                y_control -= 20
                fileobj.line(20, y_control, 570, y_control)
                y_control -= 20
                fileobj.drawString(120, y_control, "Difference")
                if difference < 0:
                    difference = str(difference).replace("-", "")
                    fileobj.drawString(
                        RPTHandler.calculate_x(400, difference),
                        y_control,
                        "%.2f" % float(difference),
                    )
                else:
                    fileobj.drawString(
                        RPTHandler.calculate_x(510, str(difference)),
                        y_control,
                        "%.2f" % float(difference),
                    )

        else:
            fileobj.setFont("Helvetica-Bold", 11)
            fileobj.drawString(240, 650, "No Record Found")

        fileobj.showPage()
        fileobj.save()

        TBDefault.chart_accounts = []

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return buffer

    def export_tb_csv(
        division,
        tb_type=None,
        year=None,
        month=None,
        debits=None,
        credits=None,
        as_of_date=None,
        zero_value=None
    ):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        comp_format = workbook.add_format({"bold": True, "align": "left"})
        title_format = workbook.add_format({"bold": True, "align": "center"})

        report_title = TBDefault.fetchTitle(
            tb_type=tb_type, year=year, month=month, as_of_date=as_of_date
        )

        title_format.set_font_size(16)
        worksheet.merge_range("D4:G4", report_title, title_format)

        worksheet.write("D6", "A/c #", comp_format)
        worksheet.write("E6", "Account Name", comp_format)
        worksheet.write("F6", "Debit", comp_format)
        worksheet.write("G6", "Credit", comp_format)

        worksheet.set_column(4, 6, 15)

        if len(TBDefault.chart_accounts) > 0:

            TBDefault.render_csv_accounts(
                workbook, worksheet, TBDefault.chart_accounts, 7, debits, credits, zero_value
            )

        else:

            record_format = workbook.add_format({"bold": True, "align": "center"})
            record_format.set_font_size(12)
            worksheet.merge_range("D8:G8", "No Record Found", record_format)

        workbook.close()
        buffer.seek(0)

        return buffer
