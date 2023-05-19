##for file handling
import io

import xlsxwriter
from django.conf import settings
from django.db.models import Q

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

CAT_NAMES = {
    "Income": "Income",
    "COGS": "Direct Cost / COGS",
    "Expense": "Operating Expenses",
}


class IEGeneral:

    # for managing accounts
    chart_accounts = []
    child_accounts = []

    # for totals
    type_totals = {}

    # file handling objects
    pdfBuffer = ""
    pdfFileObj = ""
    pdfYControl = 660

    # file handling objects for csv
    csvBuffer = ""
    csv_workbook = ""
    csv_worksheet = ""
    csv_cell_ref = 3

    def get_accounts(division, category, rpt_code=None):
        IEGeneral.chart_accounts.clear()
        coa_obj = T01Coa10.objects

        if rpt_code == "PL":
            coa_obj = coa_obj.exclude(account_num="999C")

        if category == "Income" or category == "Expense":
            if category == "Income":
                group = "3"
            else:
                group = "4"

            IEGeneral.pre_transversal(
                coa_obj.filter(
                    ~Q(account_type="4"),
                    account_group=group,
                    division__division_name=division,
                    parent=None,
                ),
                division,
                True,
                IEGeneral.chart_accounts,
                rpt_code
            )
        else:
            IEGeneral.pre_transversal(
                coa_obj.filter(
                    account_type="4", division__division_name=division
                ),
                division,
                False,
                IEGeneral.chart_accounts,
                rpt_code
            )

        return IEGeneral.chart_accounts

    def pre_transversal(accounts, division, exclude, source_location, rpt_code=None):
        coa_obj = T01Coa10.objects

        if rpt_code == "PL":
            coa_obj = coa_obj.exclude(account_num="999C")

        for acc in accounts:
            if acc in source_location:
                print("Already exists")
            else:
                source_location.append(acc)
            if exclude == True:
                acc_list = coa_obj.filter(
                    ~Q(account_type="4"),
                    parent=acc.id,
                    division__division_name=division,
                )
            else:
                acc_list = coa_obj.filter(
                    parent=acc.id, division__division_name=division
                )
            IEGeneral.pre_transversal(acc_list, division, exclude, source_location, rpt_code)

    # for generating title for the report
    def fetchTitle(tb_type=None, year=None, month=None, as_of_date=None):
        if as_of_date:
            report_title = f"Income / Expense Sheet as of {as_of_date.strftime(settings.DATE_INPUT_FORMATS[0])}"
        else:
            if tb_type == "1":
                report_title = "Annual Opening Income / Expense Sheet as of "
            elif tb_type == "2":
                report_title = "Annual Closing Income / Expense Sheet as of "
            elif tb_type == "3":
                report_title = "Income / Expense Sheet as of "

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
    def set_pdf_headers(y_axis, year):
        IEGeneral.pdfFileObj.setFont("Helvetica-Bold", 13)
        IEGeneral.pdfFileObj.drawString(30, y_axis, "A/c #")
        IEGeneral.pdfFileObj.drawString(95, y_axis, "Account Name")
        IEGeneral.pdfFileObj.drawString(430, y_axis, str(year) if year else "")
        IEGeneral.pdfFileObj.line(20, y_axis - 15, 570, y_axis - 15)

    # generation of report headers
    def set_csv_headers(cell_ref, year):
        header_format = IEGeneral.csv_workbook.add_format(
            {"bold": True, "align": "left"}
        )
        header_format.set_font(12)
        IEGeneral.csv_worksheet.write("D" + str(cell_ref), "A/c #", header_format)
        IEGeneral.csv_worksheet.write(
            "E" + str(cell_ref), "Account Name", header_format
        )
        IEGeneral.csv_worksheet.write(
            "F" + str(cell_ref), str(year) if year else "", header_format
        )

    def handleNegative(value):
        value = str(value)
        if float(value) < 0:
            IEGeneral.pdfFileObj.drawString(
                RPTHandler.calculate_x(430, value),
                IEGeneral.pdfYControl,
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
            )
        else:
            IEGeneral.pdfFileObj.drawString(
                RPTHandler.calculate_x(430, value),
                IEGeneral.pdfYControl,
                "%.2f" % float(value),
            )

    def setUpTotal(title, total_value):
        IEGeneral.pdfYControl -= 20
        IEGeneral.pdfFileObj.setFont("Helvetica-Bold", 12)
        IEGeneral.pdfFileObj.drawString(170, IEGeneral.pdfYControl, title)
        IEGeneral.handleNegative(str(total_value))

    # for initailising pdf file
    def initiationPDF(company, tb_type=None, year=None, month=None, as_of_date=None):
        # Create a file-like IEGeneral.pdfBuffer to receive PDF data.
        IEGeneral.pdfBuffer = io.BytesIO()
        IEGeneral.type_totals = {"Income": 0, "COGS": 0, "Expense": 0}

        # Create the PDF object, using the IEGeneral.pdfBuffer as its "file."
        IEGeneral.pdfFileObj = canvas.Canvas(IEGeneral.pdfBuffer)

        RPTHandler.set_comp_header(True, company, IEGeneral.pdfFileObj)

        report_title = IEGeneral.fetchTitle(
            tb_type=tb_type, year=year, month=month, as_of_date=as_of_date
        )

        IEGeneral.pdfFileObj.setFont("Helvetica", 17)
        IEGeneral.pdfFileObj.drawString(110, 730, report_title)
        IEGeneral.pdfFileObj.line(20, 710, 570, 710)

        IEGeneral.set_pdf_headers(685, year)

    # for initailising pdf file
    def initiationCSV(tb_type=None, year=None, month=None, as_of_date=None):

        IEGeneral.csvBuffer = io.BytesIO()

        IEGeneral.csv_workbook = xlsxwriter.Workbook(IEGeneral.csvBuffer)
        IEGeneral.csv_worksheet = IEGeneral.csv_workbook.add_worksheet()

        title_format = IEGeneral.csv_workbook.add_format(
            {"bold": True, "align": "left"}
        )

        report_title = IEGeneral.fetchTitle(
            tb_type=tb_type, year=year, month=month, as_of_date=as_of_date
        )

        title_format.set_font_size(16)
        IEGeneral.csv_worksheet.merge_range("D4:F4", report_title, title_format)

        IEGeneral.set_csv_headers(6, year)
        IEGeneral.csv_cell_ref = 7

    def render_accounts(accounts, amounts, year, type):
        IEGeneral.pdfYControl -= 20
        IEGeneral.pdfFileObj.setFont("Helvetica-Bold", 12)
        IEGeneral.pdfFileObj.drawString(30, IEGeneral.pdfYControl, CAT_NAMES[type])
        IEGeneral.pdfYControl -= 25
        if len(accounts) > 0:
            for account in accounts:
                x_shift = 95
                IEGeneral.pdfFileObj.setFont("Helvetica", 11)
                for val in range(0, account.level):
                    x_shift += 10
                IEGeneral.pdfFileObj.drawString(
                    30, IEGeneral.pdfYControl, account.account_num
                )
                IEGeneral.pdfFileObj.drawString(
                    x_shift, IEGeneral.pdfYControl, account.account_name
                )
                if account.coa_control == "1":
                    IEGeneral.pdfFileObj.setFont("Helvetica-Bold", 11)
                else:
                    IEGeneral.type_totals[type] += float(amounts[account.id])
                if account.level != 0:
                    IEGeneral.handleNegative(amounts[account.id])
                IEGeneral.pdfYControl -= 20
                if IEGeneral.pdfYControl <= 15:
                    IEGeneral.pdfFileObj.showPage()
                    IEGeneral.pdfYControl = 760
                    IEGeneral.set_pdf_headers(800, year)

            IEGeneral.pdfFileObj.line(
                160, IEGeneral.pdfYControl, 500, IEGeneral.pdfYControl
            )
            IEGeneral.setUpTotal("Total", IEGeneral.type_totals[type])

            total_income = "%.2f" % float(IEGeneral.type_totals["Income"])
            total_cogs = "%.2f" % float(IEGeneral.type_totals["COGS"])
            total_expense = "%.2f" % float(IEGeneral.type_totals["Expense"])

            if type == "COGS":
                IEGeneral.setUpTotal(
                    "Gross Income",
                    float(total_income) - float(total_cogs),
                )
            elif type == "Expense":
                IEGeneral.pdfYControl -= 20
                IEGeneral.pdfFileObj.line(
                    20, IEGeneral.pdfYControl, 570, IEGeneral.pdfYControl
                )
                IEGeneral.setUpTotal(
                    "Net Profit/Loss",
                    float(total_income)
                    - float(total_cogs)
                    - float(total_expense),
                )
        else:
            IEGeneral.pdfFileObj.setFont("Helvetica-Bold", 11)
            IEGeneral.pdfFileObj.drawString(
                240, IEGeneral.pdfYControl, "No Record Found"
            )
            IEGeneral.pdfYControl -= 15

    def render_csv_accounts(accounts, amounts, type):
        cell_left_format = IEGeneral.csv_workbook.add_format({"align": "left"})
        cell_right_format = IEGeneral.csv_workbook.add_format({"align": "right"})
        bold_cell_right_format = IEGeneral.csv_workbook.add_format(
            {"bold": True, "align": "right"}
        )
        bold_cell_left_format = IEGeneral.csv_workbook.add_format(
            {"bold": True, "align": "left"}
        )
        bold_cell_center_format = IEGeneral.csv_workbook.add_format(
            {"bold": True, "align": "center"}
        )
        IEGeneral.csv_worksheet.merge_range(
            "D" + str(IEGeneral.csv_cell_ref) + ":H" + str(IEGeneral.csv_cell_ref),
            CAT_NAMES[type],
            bold_cell_left_format,
        )
        IEGeneral.csv_cell_ref += 1
        if len(accounts) > 0:
            for account in accounts:
                IEGeneral.csv_worksheet.write(
                    "D" + str(IEGeneral.csv_cell_ref),
                    account.account_num,
                    cell_left_format,
                )
                if account.coa_control == "1":
                    value = str(amounts[account.id])
                    if float(value) < 0:
                        IEGeneral.csv_worksheet.write(
                            "F" + str(IEGeneral.csv_cell_ref),
                            "(" + "%.2f" % float(value.replace("-", "")) + ")",
                            bold_cell_right_format,
                        )
                    else:
                        IEGeneral.csv_worksheet.write(
                            "F" + str(IEGeneral.csv_cell_ref),
                            "%.2f" % float(value),
                            bold_cell_right_format,
                        )
                else:
                    value = str(amounts[account.id])
                    if float(value) < 0:
                        IEGeneral.csv_worksheet.write(
                            "F" + str(IEGeneral.csv_cell_ref),
                            "(" + "%.2f" % float(value.replace("-", "")) + ")",
                            cell_right_format,
                        )
                    else:
                        IEGeneral.csv_worksheet.write(
                            "F" + str(IEGeneral.csv_cell_ref),
                            "%.2f" % float(value),
                            cell_right_format,
                        )
                width = len(account.account_name) + 15
                IEGeneral.csv_worksheet.set_column(4, IEGeneral.csv_cell_ref, width)
                IEGeneral.csv_worksheet.write(
                    "E" + str(IEGeneral.csv_cell_ref),
                    account.account_name,
                    cell_left_format,
                )
                IEGeneral.csv_cell_ref += 1
        else:
            IEGeneral.csv_worksheet.merge_range(
                "D" + str(IEGeneral.csv_cell_ref) + ":F" + str(IEGeneral.csv_cell_ref),
                "No Record Found",
                bold_cell_center_format,
            )
            IEGeneral.csv_cell_ref += 1

    # for generating template of pdf
    def export_ie_pdf():

        IEGeneral.pdfFileObj.showPage()
        IEGeneral.pdfFileObj.save()

        IEGeneral.pdfYControl = 660
        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        IEGeneral.pdfBuffer.seek(0)
        return IEGeneral.pdfBuffer

    def export_ie_csv(division, tb_type, year, month):

        IEGeneral.csv_workbook.close()
        IEGeneral.csvBuffer.seek(0)

        return IEGeneral.csvBuffer
