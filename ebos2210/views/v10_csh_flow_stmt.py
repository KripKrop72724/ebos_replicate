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

MONTH_NAMES = [
    "",
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

MONTH_ABV_NAMES = [
    "",
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


class CshFlowStmt:

    pdf_file_obj = ""
    pdf_buffer = ""
    pdf_YControl = 0

    def month_range_handler(x_index, y_index, balance, month):
        x = month
        for index in range(0, 12):
            balance_value = balance[index]
            if balance_value < 0:
                CshFlowStmt.pdf_file_obj.drawString(
                    RPTHandler.calculate_small_x(x_index, str(balance_value), 4),
                    y_index,
                    "(" + "%.2f" % float(str(balance_value).replace("-", "")) + ")",
                )
            else:
                CshFlowStmt.pdf_file_obj.drawString(
                    RPTHandler.calculate_small_x(x_index, str(balance_value), 4),
                    y_index,
                    "%.2f" % float((balance_value)),
                )
            x += 1
            x_index += 54
            if x == 13:
                x = 1

    # generation of report headers
    def set_pdf_headers(y_axis, month, year):
        CshFlowStmt.pdf_file_obj.setFont("Helvetica-Bold", 10)
        CshFlowStmt.pdf_file_obj.drawString(15, y_axis, "Cash Flow")
        CshFlowStmt.pdf_file_obj.drawString(70, y_axis, "Desc")
        x_index = 140
        x = month
        for index in range(0, 12):
            CshFlowStmt.pdf_file_obj.drawString(
                x_index, y_axis, MONTH_ABV_NAMES[x] + "-" + str(year)[2:4]
            )
            x += 1
            x_index += 54
            if x == 13:
                x = 1
                year += 1
        CshFlowStmt.pdf_file_obj.line(10, y_axis - 15, 780, y_axis - 15)

    def initPDF(company, month, year, opening_balance):

        # Create a file-like buffer to receive PDF data.
        CshFlowStmt.pdf_buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its 'file.'
        CshFlowStmt.pdf_file_obj = canvas.Canvas(
            CshFlowStmt.pdf_buffer, pagesize=(landscape(letter))
        )

        RPTHandler.set_comp_header_landscape(True, company, CshFlowStmt.pdf_file_obj)

        CshFlowStmt.pdf_file_obj.setFont("Helvetica", 13)
        CshFlowStmt.pdf_file_obj.drawString(310, 515, "Cash Flow Statement")
        CshFlowStmt.pdf_file_obj.line(310, 510, 434, 510)

        CshFlowStmt.pdf_file_obj.setFont("Helvetica-Bold", 11)
        CshFlowStmt.pdf_file_obj.drawString(320, 490, "From :")

        CshFlowStmt.pdf_file_obj.setFont("Helvetica", 10)
        width = len(MONTH_NAMES[month]) * 5 + 10
        CshFlowStmt.pdf_file_obj.drawString(360, 490, MONTH_NAMES[month])
        CshFlowStmt.pdf_file_obj.drawString(360 + width, 490, str(year))

        CshFlowStmt.pdf_file_obj.line(10, 470, 780, 470)

        CshFlowStmt.set_pdf_headers(450, month, year)

        CshFlowStmt.pdf_YControl = 415
        CshFlowStmt.pdf_file_obj.drawString(
            15, CshFlowStmt.pdf_YControl, "Opening Balance"
        )
        CshFlowStmt.pdf_file_obj.setFont("Helvetica", 8)
        CshFlowStmt.month_range_handler(
            155, CshFlowStmt.pdf_YControl, opening_balance, month
        )
        CshFlowStmt.pdf_YControl -= 20

    # to render the items under cash flow
    def render_flow_desc(flow, style):
        CshFlowStmt.pdf_file_obj.setFont(style, 8)
        CshFlowStmt.pdf_file_obj.drawString(
            15, CshFlowStmt.pdf_YControl, str(flow.cashflow_desc)
        )
        CshFlowStmt.pdf_YControl -= 20

    # to render the items under cash flow
    def render_flow_records(account, balance, month, year):
        CshFlowStmt.pdf_file_obj.setFont("Helvetica", 8)
        CshFlowStmt.pdf_file_obj.drawString(
            15, CshFlowStmt.pdf_YControl, "    " + str(account.account_name)
        )
        CshFlowStmt.month_range_handler(155, CshFlowStmt.pdf_YControl, balance, month)
        CshFlowStmt.pdf_YControl -= 20
        if CshFlowStmt.pdf_YControl <= 20:
            CshFlowStmt.pdf_file_obj.showPage()
            CshFlowStmt.pdf_YControl = 520
            CshFlowStmt.set_pdf_headers(560, month, year)

    def render_sub_total(totals, month):
        CshFlowStmt.pdf_YControl += 20
        CshFlowStmt.month_range_handler(155, CshFlowStmt.pdf_YControl, totals, month)
        CshFlowStmt.pdf_YControl -= 20

    def render_cat_total(flow_record, flow_total, month):
        CshFlowStmt.pdf_file_obj.line(
            10, CshFlowStmt.pdf_YControl, 780, CshFlowStmt.pdf_YControl
        )
        CshFlowStmt.pdf_YControl -= 15
        CshFlowStmt.month_range_handler(
            155, CshFlowStmt.pdf_YControl, flow_total, month
        )
        CshFlowStmt.pdf_file_obj.setFont("Helvetica-Bold", 9)
        CshFlowStmt.pdf_file_obj.drawString(
            15, CshFlowStmt.pdf_YControl, str(flow_record.cashflow_desc) + " Total"
        )
        CshFlowStmt.pdf_YControl -= 15
        CshFlowStmt.pdf_file_obj.line(
            10, CshFlowStmt.pdf_YControl, 780, CshFlowStmt.pdf_YControl
        )
        CshFlowStmt.pdf_YControl -= 20

    def render_stmt_items(items, month, year):
        for item in items:
            CshFlowStmt.render_flow_desc(item["detail"], "Helvetica-Bold")
            for sub_item in item["sub_flows"]:
                CshFlowStmt.render_flow_desc(sub_item["detail"], "Helvetica")
                CshFlowStmt.render_sub_total(sub_item["balance"], month)
                for account in sub_item["accounts"]:
                    CshFlowStmt.render_flow_records(
                        account["detail"], account["balance"], month, year
                    )
            CshFlowStmt.render_cat_total(item["detail"], item["balance"], month)

    # for generating template of pdf
    def export_cfs_pdf(cash_flows, month, year, closing_balance):

        CshFlowStmt.pdf_file_obj.setFont("Helvetica", 8)
        CshFlowStmt.month_range_handler(
            155, CshFlowStmt.pdf_YControl, closing_balance, month
        )
        CshFlowStmt.pdf_file_obj.setFont("Helvetica-Bold", 10)
        CshFlowStmt.pdf_file_obj.drawString(
            15, CshFlowStmt.pdf_YControl, "Closing Balance"
        )
        CshFlowStmt.pdf_YControl -= 20

        CshFlowStmt.pdf_file_obj.showPage()
        CshFlowStmt.pdf_file_obj.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        CshFlowStmt.pdf_buffer.seek(0)
        return CshFlowStmt.pdf_buffer

    def export_cfs_csv():

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
