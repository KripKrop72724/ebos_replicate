from django.db.models import Q

from .v10_tb_default import *


class CTBDefault(TBDefault):

    CELL_REF = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]
    ACC_TYPE = ["Rollup", "Postable"]
    div_cat_totals = []

    # fetching accounts without nested structure
    def get_all_div_accounts(division, base_group):
        TBDefault.chart_accounts = []
        base_accounts = T01Coa10.objects.filter(
            account_group=base_group, division__division_name=division, parent=None
        )
        if base_accounts.count() > 0:
            base_id = base_accounts[0].id
            accounts = T01Coa10.objects.filter(
                division__division_name=division, parent=base_id
            )
            TBDefault.pre_transversal(accounts, division)
        return TBDefault.chart_accounts

    # for generating template of pdf
    def export_ctb_pdf():

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object'','' using the buffer as its "file."
        fileobj = canvas.Canvas(buffer)

        fileobj.showPage()
        fileobj.save()
        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return buffer

    def set_excel_headers(worksheet, ROW_TRIGGER, COL_TRIGGER, bold, Cols, divisions):
        for col in Cols:
            width = len(col) + 10
            worksheet.set_column(COL_TRIGGER, ROW_TRIGGER, width)
            worksheet.write(
                CTBDefault.CELL_REF[COL_TRIGGER] + str(ROW_TRIGGER), col, bold
            )
            COL_TRIGGER += 1
        for division in divisions:
            width = len(str(division)) + 10
            worksheet.set_column(COL_TRIGGER, ROW_TRIGGER, width)
            worksheet.write(
                CTBDefault.CELL_REF[COL_TRIGGER] + str(ROW_TRIGGER), str(division), bold
            )
            COL_TRIGGER += 1

    def set_total_structure(divisions):
        CTBDefault.div_cat_totals = {}
        for division in divisions:
            CTBDefault.div_cat_totals[str(division.id)] = 0

    def show_totals(worksheet, divisions, row_index, col_index, style, division_confg):
        for division in divisions:
            if division_confg[str(division.id)] == True:
                amount = CTBDefault.div_cat_totals[str(division.id)]
                if float(amount) < 0:
                    worksheet.write(
                        CTBDefault.CELL_REF[col_index] + str(row_index),
                        "(" + "%.2f" % float(str(amount).replace("-", "")) + ")",
                        style,
                    )
                else:
                    worksheet.write(
                        CTBDefault.CELL_REF[col_index] + str(row_index),
                        "%.2f" % float(amount),
                        style,
                    )
            col_index += 1

    def set_excel_data(
        workbook,
        worksheet,
        account_infos,
        divisions,
        amounts,
        ROW_TRIGGER,
        COL_TRIGGER,
        division_confg,
    ):

        center = workbook.add_format({"align": "center"})
        right = workbook.add_format({"align": "right"})
        right_bold = workbook.add_format(
            {"align": "right", "bold": True, "font_color": "red"}
        )
        cat_style = workbook.add_format(
            {"bold": True, "align": "left", "font_color": "red", "font_size": 11}
        )
        roll_style = workbook.add_format(
            {"bold": True, "align": "left", "font_size": 11}
        )
        for account_info in account_infos:
            CTBDefault.set_total_structure(divisions)
            worksheet.write(
                CTBDefault.CELL_REF[COL_TRIGGER + 1] + str(ROW_TRIGGER),
                account_info["name"],
                cat_style,
            )
            cat_row_index = ROW_TRIGGER
            ROW_TRIGGER += 1
            for account in account_info["accounts"]:
                include = True
                if include == True:
                    worksheet.write(
                        CTBDefault.CELL_REF[COL_TRIGGER] + str(ROW_TRIGGER),
                        account.account_num,
                        center,
                    )
                    width = len(account.account_name) + 10
                    worksheet.set_column(COL_TRIGGER + 1, ROW_TRIGGER, width)
                    if account.coa_control == "1":
                        worksheet.write(
                            CTBDefault.CELL_REF[COL_TRIGGER + 1] + str(ROW_TRIGGER),
                            account.account_name,
                            roll_style,
                        )
                    else:
                        worksheet.write(
                            CTBDefault.CELL_REF[COL_TRIGGER + 1] + str(ROW_TRIGGER),
                            account.account_name,
                        )
                    worksheet.write(
                        CTBDefault.CELL_REF[COL_TRIGGER + 2] + str(ROW_TRIGGER),
                        CTBDefault.ACC_TYPE[int(account.coa_control) - 1],
                    )
                    col_index = COL_TRIGGER + 3
                    for division in divisions:
                        if (
                            account.coa_control == "1"
                            and division_confg[str(division.id)] == False
                        ):
                            pass
                        else:
                            if account.division == division:
                                if account.coa_control == "2":
                                    CTBDefault.div_cat_totals[
                                        str(division.id)
                                    ] += amounts[account.id]
                                if float(amounts[account.id]) < 0:
                                    worksheet.write(
                                        CTBDefault.CELL_REF[col_index]
                                        + str(ROW_TRIGGER),
                                        "("
                                        + "%.2f"
                                        % float(
                                            str(amounts[account.id]).replace("-", "")
                                        )
                                        + ")",
                                        right,
                                    )
                                else:
                                    worksheet.write(
                                        CTBDefault.CELL_REF[col_index]
                                        + str(ROW_TRIGGER),
                                        "%.2f" % float(amounts[account.id]),
                                        right,
                                    )
                            else:
                                worksheet.write(
                                    CTBDefault.CELL_REF[col_index] + str(ROW_TRIGGER),
                                    "0.00",
                                    right,
                                )
                        col_index += 1
                    ROW_TRIGGER += 1
            CTBDefault.show_totals(
                worksheet,
                divisions,
                cat_row_index,
                COL_TRIGGER + 3,
                right_bold,
                division_confg,
            )

    def export_ctb_csv(
        company, tb_type, year, month, divisions, accounts, amounts, division_confg
    ):
        buffer = io.BytesIO()

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        header_format = workbook.add_format({"bold": True, "align": "center"})
        comp_format = workbook.add_format(
            {"bold": True, "align": "left", "font_color": "red"}
        )
        title_format = workbook.add_format({"bold": True, "align": "left"})

        report_title = TBDefault.fetchTitle(tb_type, year, month)
        title = "Consolidated " + report_title

        comp_format.set_font_size(13)
        worksheet.merge_range("D3:H3", str(company), comp_format)
        title_format.set_font_size(15)
        worksheet.merge_range("D4:H4", report_title, title_format)

        ROW_TRIGGER = 6  # row from where rows starts
        Cols = ["A/c #", "Account Name", "Account type"]
        CTBDefault.set_excel_headers(
            worksheet, ROW_TRIGGER, 3, header_format, Cols, divisions
        )
        ROW_TRIGGER += 1

        CTBDefault.set_excel_data(
            workbook,
            worksheet,
            accounts,
            divisions,
            amounts,
            ROW_TRIGGER,
            3,
            division_confg,
        )

        workbook.close()
        buffer.seek(0)

        return buffer
