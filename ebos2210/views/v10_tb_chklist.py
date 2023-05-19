import io

import xlsxwriter
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


class TBCheckList:

    # for managing accounts
    chart_accounts = []
    child_accounts = []

    totals = {}

    def get_all_accounts(division):
        acc_1s = T01Coa10.objects.filter(
            parent=None, division__division_name=division
        ).order_by("account_group")
        TBCheckList.pre_transversal(acc_1s, division)

        return TBCheckList.chart_accounts

    def pre_transversal(accounts, division):
        for acc in accounts:
            TBCheckList.chart_accounts.append(acc)
            acc_list = T01Coa10.objects.filter(
                parent=acc.id, division__division_name=division
            )
            TBCheckList.pre_transversal(acc_list, division)

    def fetch_children(accounts, division):
        for acc in accounts:
            TBCheckList.child_accounts.append(acc)
            acc_list = T01Coa10.objects.filter(
                parent=acc.id, division__division_name=division
            )
            TBCheckList.fetch_children(acc_list, division)

    # generation of report headers
    def set_pdf_headers(canvas, y_axis):
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(30, y_axis, "A/c #")
        canvas.drawString(80, y_axis, "Account Name")
        canvas.drawString(280, y_axis + 5, "Opening")
        canvas.drawString(365, y_axis + 5, "Debit")
        canvas.drawString(435, y_axis + 5, "Credit")
        canvas.drawString(500, y_axis + 5, "Closing")
        canvas.drawString(500, y_axis - 15, "Balance")
        canvas.line(20, y_axis - 30, 570, y_axis - 30)

    def render_accounts(canvas, accounts, y_control, openings, debits, credits, month):
        for account in accounts:
            x_shift = 80
            canvas.setFont("Helvetica", 9)
            for val in range(0, account.level):
                x_shift += 10
            canvas.drawString(30, y_control, account.account_num)
            canvas.drawString(x_shift, y_control, account.account_name)
            closing = str(
                float(openings[account.id])
                + float(debits[account.id])
                - float(credits[account.id])
            )
            # showing rollsups in bold
            if account.coa_control == "1":
                canvas.setFont("Helvetica-Bold", 9)
            else:
                TBCheckList.totals["opening"] += float(openings[account.id])
                TBCheckList.totals["debit"] += float(debits[account.id])
                TBCheckList.totals["credit"] += float(credits[account.id])
                TBCheckList.totals["closing"] += float(closing)
            RPTHandler.handleSmallNegative(canvas, 305, y_control, openings[account.id])
            RPTHandler.handleSmallNegative(canvas, 385, y_control, debits[account.id])
            RPTHandler.handleSmallNegative(canvas, 455, y_control, credits[account.id])
            RPTHandler.handleSmallNegative(canvas, 530, y_control, closing)
            y_control -= 20
            if y_control <= 20:
                canvas.showPage()
                y_control = 750
                TBCheckList.set_pdf_headers(canvas, 810)
        return y_control

    # for generating template of pdf
    def export_tb_pdf(company, year, month, openings, debits, credits):

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
        TBCheckList.totals = {"opening": 0, "debit": 0, "credit": 0, "closing": 0}

        # Create the PDF object, using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        RPTHandler.set_comp_header(True, company, fileobj)
        report_title = ""

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

        fileobj.setFont("Helvetica", 18)
        fileobj.drawString(
            155, 730, f"Trial Balance check-list as of {report_title} {str(year)}"
        )
        fileobj.line(20, 710, 570, 710)

        TBCheckList.set_pdf_headers(fileobj, 685)
        if len(TBCheckList.chart_accounts) > 0:
            y_control = TBCheckList.render_accounts(
                fileobj,
                TBCheckList.chart_accounts,
                630,
                openings,
                debits,
                credits,
                month,
            )

            fileobj.line(20, y_control, 570, y_control)
            y_control -= 20

            RPTHandler.handleSmallNegative(
                fileobj, 305, y_control, TBCheckList.totals["opening"]
            )
            RPTHandler.handleSmallNegative(
                fileobj, 385, y_control, TBCheckList.totals["debit"]
            )
            RPTHandler.handleSmallNegative(
                fileobj, 455, y_control, TBCheckList.totals["credit"]
            )
            RPTHandler.handleSmallNegative(
                fileobj, 530, y_control, TBCheckList.totals["closing"]
            )

            y_control -= 10
            fileobj.line(20, y_control, 570, y_control)
            y_control -= 20

            fileobj.drawString(290, y_control, "Totals")

            debit = TBCheckList.totals["debit"]
            credit = TBCheckList.totals["credit"]

            if TBCheckList.totals["closing"] > 0:
                debit = debit - TBCheckList.totals["closing"]
                RPTHandler.handleSmallNegative(fileobj, 385, y_control, debit)
                RPTHandler.handleSmallNegative(fileobj, 455, y_control, credit)
            else:
                credit = credit + TBCheckList.totals["closing"]
                RPTHandler.handleSmallNegative(fileobj, 385, y_control, debit)
                RPTHandler.handleSmallNegative(fileobj, 455, y_control, credit)

            y_control -= 10
            difference = debit - credit
            if difference > 0:
                fileobj.line(20, y_control, 570, y_control)
                y_control -= 20
                fileobj.drawString(290, y_control, "Difference")
                if debit > credit:
                    RPTHandler.handleSmallNegative(fileobj, 385, y_control, difference)
                else:
                    RPTHandler.handleSmallNegative(fileobj, 455, y_control, difference)
        else:
            fileobj.setFont("Helvetica-Bold", 11)
            fileobj.drawString(240, 630, "No Record Found")

        fileobj.showPage()
        fileobj.save()

        TBCheckList.chart_accounts = []

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return buffer

    def export_tb_csv(division, year, month):

        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        workbook.close()
        buffer.seek(0)

        return buffer
