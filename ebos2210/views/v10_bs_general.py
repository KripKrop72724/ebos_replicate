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
    "Assets": "Assets",
    "Equities": "Shareholder's Equities",
    "Liabilities": "Liabilities",
}


class BSGeneral:

    # for managing accounts
    chart_accounts = []
    child_accounts = []

    # for totals
    type_totals = {}

    # file handling objects for pdf
    pdfBuffer = ""
    pdfFileObj = ""
    pdfYControl = 645
    # file handling objects for csv
    csvBuffer = ""
    csv_workbook = ""
    csv_worksheet = ""
    csv_cell_ref = 3

    def get_accounts(division, category):
        BSGeneral.chart_accounts.clear()
        if category == "Assets" or category == "Liabilities":
            if category == "Assets":
                group = "1"
            else:
                group = "2"
            BSGeneral.pre_transversal(
                T01Coa10.objects.filter(
                    ~Q(account_type="5"),
                    account_group=group,
                    division__division_name=division,
                    parent=None,
                ),
                division,
                True,
                BSGeneral.chart_accounts,
            )
        else:
            BSGeneral.pre_transversal(
                T01Coa10.objects.filter(
                    account_type="5", division__division_name=division
                ),
                division,
                False,
                BSGeneral.chart_accounts,
            )

        return BSGeneral.chart_accounts

    def pre_transversal(accounts, division, exclude, source_location):
        for acc in accounts:
            if acc in source_location:
                print("Already exists")
            else:
                source_location.append(acc)
            if exclude == True:
                acc_list = T01Coa10.objects.filter(
                    ~Q(account_type="5"),
                    parent=acc.id,
                    division__division_name=division,
                )
            else:
                acc_list = T01Coa10.objects.filter(
                    parent=acc.id, division__division_name=division
                )
            BSGeneral.pre_transversal(acc_list, division, exclude, source_location)

    # for generating title for the report
    def fetchTitle(tb_type=None, year=None, month=None, as_of_date=None):
        if as_of_date:
            report_title = f"Balance Sheet as of {as_of_date.strftime(settings.DATE_INPUT_FORMATS[0])}"
        else:
            if tb_type == "1":
                report_title = "Annual Opening Balance Sheet as of "
            elif tb_type == "2":
                report_title = "Annual Closing Balance Sheet as of "
            elif tb_type == "3":
                report_title = "Balance Sheet as of "

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
        BSGeneral.pdfFileObj.setFont("Helvetica-Bold", 12)
        BSGeneral.pdfFileObj.drawString(30, y_axis, "A/c #")
        BSGeneral.pdfFileObj.drawString(95, y_axis, "Account Name")
        BSGeneral.pdfFileObj.drawString(430, y_axis, str(year) if year else "")
        BSGeneral.pdfFileObj.line(20, y_axis - 15, 570, y_axis - 15)

    # generation of report headers
    def set_csv_headers(cell_ref, year):
        header_format = BSGeneral.csv_workbook.add_format(
            {"bold": True, "align": "left"}
        )
        header_format.set_font(12)
        BSGeneral.csv_worksheet.write("D" + str(cell_ref), "A/c #", header_format)
        BSGeneral.csv_worksheet.write(
            "E" + str(cell_ref), "Account Name", header_format
        )
        BSGeneral.csv_worksheet.write(
            "F" + str(cell_ref), str(year) if year else "", header_format
        )

    def handleNegative(value):
        value = str(value)
        if float(value) < 0:
            BSGeneral.pdfFileObj.drawString(
                RPTHandler.calculate_x(430, value),
                BSGeneral.pdfYControl,
                "(" + "%.2f" % float(value.replace("-", "")) + ")",
            )
        else:
            BSGeneral.pdfFileObj.drawString(
                RPTHandler.calculate_x(430, value),
                BSGeneral.pdfYControl,
                "%.2f" % float(value),
            )

    # for initailising pdf file
    def initiationPDF(company, tb_type=None, year=None, month=None, as_of_date=None):
        # Create a file-like BSGeneral.pdfBuffer to receive PDF data.
        BSGeneral.pdfBuffer = io.BytesIO()
        BSGeneral.type_totals = {"Assets": 0, "Equities": 0, "Liabilities": 0}

        # Create the PDF object, using the BSGeneral.pdfBuffer as its "file."
        BSGeneral.pdfFileObj = canvas.Canvas(BSGeneral.pdfBuffer)

        RPTHandler.set_comp_header(True, company, BSGeneral.pdfFileObj)

        report_title = BSGeneral.fetchTitle(
            tb_type=tb_type, year=year, month=month, as_of_date=as_of_date
        )

        BSGeneral.pdfFileObj.setFont("Helvetica", 17)
        BSGeneral.pdfFileObj.drawString(150, 730, report_title)
        BSGeneral.pdfFileObj.line(20, 710, 570, 710)

        BSGeneral.set_pdf_headers(685, year)
        BSGeneral.pdfYControl -= 5

    # for initailising pdf file
    def initiationCSV(tb_type=None, year=None, month=None, as_of_date=None):

        BSGeneral.csvBuffer = io.BytesIO()

        BSGeneral.csv_workbook = xlsxwriter.Workbook(BSGeneral.csvBuffer)
        BSGeneral.csv_worksheet = BSGeneral.csv_workbook.add_worksheet()

        title_format = BSGeneral.csv_workbook.add_format(
            {"bold": True, "align": "left"}
        )

        report_title = BSGeneral.fetchTitle(
            tb_type=tb_type, year=year, month=month, as_of_date=as_of_date
        )
        title_format.set_font_size(16)
        BSGeneral.csv_worksheet.merge_range("D4:F4", report_title, title_format)

        BSGeneral.set_csv_headers(6, year)
        BSGeneral.csv_cell_ref = 7

    def render_csv_accounts(accounts, amounts, year, type, zero_value=False):
        cell_left_format = BSGeneral.csv_workbook.add_format({"align": "left"})
        cell_right_format = BSGeneral.csv_workbook.add_format({"align": "right"})
        bold_cell_right_format = BSGeneral.csv_workbook.add_format(
            {"bold": True, "align": "right"}
        )
        bold_cell_left_format = BSGeneral.csv_workbook.add_format(
            {"bold": True, "align": "left"}
        )
        bold_cell_center_format = BSGeneral.csv_workbook.add_format(
            {"bold": True, "align": "center"}
        )
        BSGeneral.csv_worksheet.merge_range(
            "D" + str(BSGeneral.csv_cell_ref) + ":H" + str(BSGeneral.csv_cell_ref),
            CAT_NAMES[type],
            bold_cell_left_format,
        )
        BSGeneral.csv_cell_ref += 1
        if len(accounts) > 0:
            for account in accounts:
                if zero_value and amounts[account.id] == 0:
                    continue
                else:
                    BSGeneral.csv_worksheet.write(
                        "D" + str(BSGeneral.csv_cell_ref),
                        account.account_num,
                        cell_left_format,
                    )
                    if account.coa_control == "1":
                        value = str(amounts[account.id])
                        if float(value) < 0:
                            BSGeneral.csv_worksheet.write(
                                "F" + str(BSGeneral.csv_cell_ref),
                                "(" + "%.2f" % float(value.replace("-", "")) + ")",
                                bold_cell_right_format,
                            )
                        else:
                            BSGeneral.csv_worksheet.write(
                                "F" + str(BSGeneral.csv_cell_ref),
                                "%.2f" % float(value),
                                bold_cell_right_format,
                            )
                    else:
                        value = str(amounts[account.id])
                        if float(value) < 0:
                            BSGeneral.csv_worksheet.write(
                                "F" + str(BSGeneral.csv_cell_ref),
                                "(" + "%.2f" % float(value.replace("-", "")) + ")",
                                cell_right_format,
                            )
                        else:
                            BSGeneral.csv_worksheet.write(
                                "F" + str(BSGeneral.csv_cell_ref),
                                "%.2f" % float(value),
                                cell_right_format,
                            )
                width = len(account.account_name) + 15
                BSGeneral.csv_worksheet.set_column(4, BSGeneral.csv_cell_ref, width)
                BSGeneral.csv_worksheet.write(
                    "E" + str(BSGeneral.csv_cell_ref),
                    account.account_name,
                    cell_left_format,
                )
                BSGeneral.csv_cell_ref += 1
        else:
            BSGeneral.csv_worksheet.merge_range(
                "D" + str(BSGeneral.csv_cell_ref) + ":F" + str(BSGeneral.csv_cell_ref),
                "No Record Found",
                bold_cell_center_format,
            )
            BSGeneral.csv_cell_ref += 1

    def render_accounts(accounts, amounts, year, type, zero_value=False):
        BSGeneral.pdfFileObj.setFont("Helvetica-Bold", 12)
        BSGeneral.pdfFileObj.drawString(30, BSGeneral.pdfYControl, CAT_NAMES[type])
        BSGeneral.pdfYControl -= 20
        if len(accounts) > 0:
            for account in accounts:
                if zero_value and amounts[account.id] == 0:
                    continue
                else:
                    x_shift = 95
                    BSGeneral.pdfFileObj.setFont("Helvetica", 11)
                    for val in range(0, account.level):
                        x_shift += 10
                    BSGeneral.pdfFileObj.drawString(
                        30, BSGeneral.pdfYControl, account.account_num
                    )
                    BSGeneral.pdfFileObj.drawString(
                        x_shift, BSGeneral.pdfYControl, account.account_name
                    )
                    if account.coa_control == "1":
                        BSGeneral.pdfFileObj.setFont("Helvetica-Bold", 11)
                    else:
                        BSGeneral.type_totals[type] += float(amounts[account.id])
                    if account.level != 0:
                        BSGeneral.handleNegative(amounts[account.id])
                    BSGeneral.pdfYControl -= 20
                    if BSGeneral.pdfYControl <= 15:
                        BSGeneral.pdfFileObj.showPage()
                        BSGeneral.pdfYControl = 760
                        BSGeneral.set_pdf_headers(800, year)

            BSGeneral.pdfFileObj.line(
                160, BSGeneral.pdfYControl, 500, BSGeneral.pdfYControl
            )
            BSGeneral.pdfYControl -= 20
            BSGeneral.pdfFileObj.setFont("Helvetica-Bold", 12)
            BSGeneral.pdfFileObj.drawString(170, BSGeneral.pdfYControl, "Total")
            BSGeneral.handleNegative(str(BSGeneral.type_totals[type]))
            BSGeneral.pdfYControl -= 20
        else:
            BSGeneral.pdfFileObj.setFont("Helvetica-Bold", 11)
            BSGeneral.pdfFileObj.drawString(
                220, BSGeneral.pdfYControl, "No Record Found"
            )
            BSGeneral.pdfYControl -= 15

    # for generating template of pdf
    def export_bs_pdf():

        if (
            BSGeneral.type_totals["Equities"] + BSGeneral.type_totals["Liabilities"]
        ) > 0:
            BSGeneral.pdfFileObj.line(
                20, BSGeneral.pdfYControl, 570, BSGeneral.pdfYControl
            )
            BSGeneral.pdfYControl -= 20
            BSGeneral.pdfFileObj.drawString(
                150, BSGeneral.pdfYControl, "Total Liabilities and Equities"
            )
            BSGeneral.handleNegative(
                str(
                    BSGeneral.type_totals["Equities"]
                    + BSGeneral.type_totals["Liabilities"]
                )
            )
            BSGeneral.pdfYControl -= 20
        
        total_assets = "%.2f" % float(BSGeneral.type_totals["Assets"])
        total_equities = "%.2f" % float(BSGeneral.type_totals["Equities"])
        total_liabilites = "%.2f" % float(BSGeneral.type_totals["Liabilities"])
        
        difference = float(total_assets) - (
            float(total_equities) + float(total_liabilites)
        )
        if difference != 0:
            BSGeneral.pdfFileObj.line(
                20, BSGeneral.pdfYControl, 570, BSGeneral.pdfYControl
            )
            BSGeneral.pdfYControl -= 20
            BSGeneral.pdfFileObj.drawString(150, BSGeneral.pdfYControl, "Difference")
            BSGeneral.handleNegative(str(difference))

        BSGeneral.pdfFileObj.showPage()
        BSGeneral.pdfFileObj.save()

        BSGeneral.pdfYControl = 645

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        BSGeneral.pdfBuffer.seek(0)
        return BSGeneral.pdfBuffer

    def export_bs_csv(division, tb_type, year, month):

        BSGeneral.csv_workbook.close()
        BSGeneral.csvBuffer.seek(0)

        return BSGeneral.csvBuffer
