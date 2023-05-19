from datetime import datetime, timedelta
from decimal import Decimal

from django.core.files.storage import default_storage

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2201.utils import get_fin_period, get_last_day_of_month
from ebos2210.models.m10_fin_gl import T10Cfg10
from ebos2210.models.m10_fin_link import T10Abs10, T10Gld10
from ebos2210.utils.u10_rpt_handler import RPTHandler
from ebos2210.views.v10_bs_general import BSGeneral
from ebos2210.views.v10_cons_tb_default import CTBDefault
from ebos2210.views.v10_csh_flow_stmt import CshFlowStmt
from ebos2210.views.v10_ie_general import IEGeneral
from ebos2210.views.v10_tb_chklist import TBCheckList
from ebos2210.views.v10_tb_default import TBDefault
from ebos2201.utils import get_path


def glr_balance(instance):
    if instance.rpt_code == "TB":
        # functionality for Trial Balance
        name = "trial_balance"
        # fetch all accounts
        chart_accounts = TBDefault.get_all_accounts(instance.division)

        # retrieve figures for accounts
        debits_dict, credits_dict = {}, {}
        for account in chart_accounts:
            TBDefault.child_accounts.clear()
            # for postable only
            if account.coa_control == "2":
                (
                    debits_dict[account.id],
                    credits_dict[account.id],
                ) = T10Abs10.coa_bal_by_rpt_type(
                    account.id, instance.year, instance.month, instance.type_of_rpt
                )
            else:
                TBDefault.fetch_children([account], instance.division)
                debit, credit = 0, 0
                for child_acc in TBDefault.child_accounts:
                    debit1, credit1 = T10Abs10.coa_bal_by_rpt_type(
                        child_acc.id,
                        instance.year,
                        instance.month,
                        instance.type_of_rpt,
                    )
                    debit += float(debit1)
                    credit += float(credit1)
                debits_dict[account.id], credits_dict[account.id] = str(debit), str(
                    credit
                )

        # calling function to create Xlsx file
        csv_data = TBDefault.export_tb_csv(
            instance.division,
            instance.type_of_rpt,
            instance.year,
            instance.month,
            debits_dict,
            credits_dict,
            zero_value=instance.without_zero_value
        )

        # calling function to create PDF
        pdf_data = TBDefault.export_tb_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.type_of_rpt,
            instance.year,
            instance.month,
            debits_dict,
            credits_dict,
            zero_value=instance.without_zero_value
        )

    elif instance.rpt_code == "BS":
        # balance sheet functionality
        name = "balance_sheet"
        # initialising pdf generation
        BSGeneral.initiationPDF(
            T01Div10.get_div_comp(instance.division),
            instance.type_of_rpt,
            instance.year,
            instance.month,
        )
        BSGeneral.initiationCSV(instance.type_of_rpt, instance.year, instance.month)

        # for managing figures
        amount_dict = {}

        # fetch all accounts
        account_types = ["Assets", "Equities", "Liabilities"]
        for type in account_types:
            chart_accounts = BSGeneral.get_accounts(instance.division, type)
            for account in chart_accounts:
                # for postable only
                amount1, amount2 = 0, 0
                if account.coa_control == "2":
                    amount1, amount2 = T10Abs10.coa_bal_by_rpt_type(
                        account.id, instance.year, instance.month, instance.type_of_rpt
                    )
                else:
                    BSGeneral.child_accounts.clear()
                    if type == "Equities":
                        BSGeneral.pre_transversal(
                            [account],
                            instance.division,
                            False,
                            BSGeneral.child_accounts,
                        )
                    else:
                        BSGeneral.pre_transversal(
                            [account], instance.division, True, BSGeneral.child_accounts
                        )
                    temp1, temp2 = 0, 0
                    for child in BSGeneral.child_accounts:
                        temp1, temp2 = T10Abs10.coa_bal_by_rpt_type(
                            child.id,
                            instance.year,
                            instance.month,
                            instance.type_of_rpt,
                        )
                        amount1 += float(temp1)
                        amount2 += float(temp2)
                amount_dict[account.id] = float(amount1) + float(amount2)

                if type == "Liabilities" or type == "Equities":
                    # if amount_dict[account.id] > 0:
                    amount_dict[account.id] *= -1

            BSGeneral.render_accounts(chart_accounts, amount_dict, instance.year, type, instance.without_zero_value)
            BSGeneral.render_csv_accounts(
                chart_accounts, amount_dict, instance.year, type, instance.without_zero_value
            )
            chart_accounts.clear()

        # calling function to create Xlsx file
        csv_data = BSGeneral.export_bs_csv(
            instance.division, instance.type_of_rpt, instance.year, instance.month
        )
        # calling function to create PDF
        pdf_data = BSGeneral.export_bs_pdf()

    elif instance.rpt_code == "PL":
        # Profit loss functionality
        name = "profit_loss"
        # initialising pdf generation
        IEGeneral.initiationPDF(
            T01Div10.get_div_comp(instance.division),
            instance.type_of_rpt,
            instance.year,
            instance.month,
        )
        IEGeneral.initiationCSV(instance.type_of_rpt, instance.year, instance.month)

        amount_dict = {}
        account_types = ["Income", "COGS", "Expense"]

        for type in account_types:
            chart_accounts = IEGeneral.get_accounts(instance.division, type, rpt_code=instance.rpt_code)
            for account in chart_accounts:
                # for postable only
                amount1, amount2 = 0, 0
                if account.coa_control == "2":
                    amount1, amount2 = T10Abs10.coa_bal_by_rpt_type(
                        account.id, instance.year, instance.month, instance.type_of_rpt
                    )
                else:
                    IEGeneral.child_accounts.clear()
                    if type == "COGS":
                        IEGeneral.pre_transversal(
                            [account],
                            instance.division,
                            False,
                            IEGeneral.child_accounts,
                        )
                    else:
                        IEGeneral.pre_transversal(
                            [account], instance.division, True, IEGeneral.child_accounts
                        )
                    temp1, temp2 = 0, 0
                    for child in IEGeneral.child_accounts:
                        temp1, temp2 = T10Abs10.coa_bal_by_rpt_type(
                            child.id,
                            instance.year,
                            instance.month,
                            instance.type_of_rpt,
                        )
                        amount1 += float(temp1)
                        amount2 += float(temp2)
                amount_dict[account.id] = float(amount1) + float(amount2)

                if type == "Income":
                    if amount_dict[account.id] < 0:
                        amount_dict[account.id] *= -1

            IEGeneral.render_accounts(chart_accounts, amount_dict, instance.year, type)
            IEGeneral.render_csv_accounts(chart_accounts, amount_dict, type)

        # calling function to create Xlsx file
        csv_data = IEGeneral.export_ie_csv(
            instance.division, instance.type_of_rpt, instance.year, instance.month
        )
        # calling function to create PDF
        pdf_data = IEGeneral.export_ie_pdf()

    elif instance.rpt_code == "TBC":

        # Trial balance checklist functionality
        name = "trial_balance_checklist"

        chart_accounts = TBCheckList.get_all_accounts(instance.division)
        currency = RPTHandler.manageNestedValues(instance.division.currency, "id")
        opening_dict, debits_dict, credits_dict = {}, {}, {}
        month = instance.month

        if month in range(13, 19):
            if month == 13:
                period = range(1, 3)
            elif month == 14:
                period = range(4, 6)
            elif month == 15:
                period = range(7, 9)
            elif month == 16:
                period = range(10, 12)
            elif month == 17:
                period = range(1, 6)
            else:
                period = range(7, 12)
        else:
            date = datetime(instance.year, month, 1)

        for account in chart_accounts:
            TBCheckList.child_accounts.clear()

            # for postable only
            if account.coa_control == "2":
                if month not in range(13, 19):
                    opening_dict[account.id] = T10Abs10.coa_opening_bal(
                        account.id, date, currency
                    )
                    (
                        debits_dict[account.id],
                        credits_dict[account.id],
                    ) = T10Gld10.gld_mtd_balance(
                        instance.division,
                        account.id,
                        instance.year,
                        month,
                        get_last_day_of_month(date).day,
                    )
                else:
                    (
                        opening_dict[account.id],
                        debits_dict[account.id],
                        credits_dict[account.id],
                    ) = (0, 0, 0)
                    for mnt in period:
                        date = datetime(instance.year, mnt, 1)
                        opening_dict[account.id] += T10Abs10.coa_opening_bal(
                            account.id, date, currency
                        )
                        a, b = T10Gld10.gld_mtd_balance(
                            instance.division,
                            account.id,
                            instance.year,
                            mnt,
                            get_last_day_of_month(date).day,
                        )
                        debits_dict[account.id] += a
                        credits_dict[account.id] += b
            else:
                TBCheckList.fetch_children([account], instance.division)
                opening, debit, credit = 0.00, 0.00, 0.00
                for child_acc in TBCheckList.child_accounts:
                    if month not in range(13, 19):
                        opening1 = T10Abs10.coa_opening_bal(
                            child_acc.id, date, currency
                        )
                        debit1, credit1 = T10Gld10.gld_mtd_balance(
                            instance.division,
                            child_acc.id,
                            instance.year,
                            month,
                            get_last_day_of_month(date).day,
                        )
                    else:
                        opening1, debit1, credit1 = 0, 0, 0
                        for mnt in period:
                            date = datetime(instance.year, mnt, 1)
                            opening1 = T10Abs10.coa_opening_bal(
                                child_acc.id, date, currency
                            )
                            a, b = T10Gld10.gld_mtd_balance(
                                instance.division,
                                child_acc.id,
                                instance.year,
                                mnt,
                                get_last_day_of_month(date).day,
                            )
                            debit1 += a
                            credit1 += b

                    debit += float(debit1)
                    credit += float(credit1)
                    opening += float(opening1)
                (
                    opening_dict[account.id],
                    debits_dict[account.id],
                    credits_dict[account.id],
                ) = (str(opening), str(debit), str(credit))

        # calling function to create Xlsx file
        csv_data = TBCheckList.export_tb_csv(instance.division, instance.year, month)

        # calling function to create PDF
        pdf_data = TBCheckList.export_tb_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.year,
            month,
            opening_dict,
            debits_dict,
            credits_dict,
        )

    elif instance.rpt_code == "CTB":
        name = "consolidated_trial_balance"
        # retrieve figures for accounts , for configiration of a division
        amount_dict, division_confg = {}, {}
        coa_accounts, base_groups, base_accounts = (
            [],
            ["1", "2", "3", "4"],
            {"1": "Assets", "2": "Liabilities", "3": "Income", "4": "Expense"},
        )
        divisions = T01Div10.objects.filter(company=instance.company)

        for division in divisions:
            confg = T10Cfg10.objects.filter(division=division)
            if confg.count() > 0:
                division_confg[str(division.id)] = confg[0].print_rollup_tot
            else:
                division_confg[str(division.id)] = False

        for base in base_groups:
            account_spec = {"name": base_accounts[base], "accounts": []}
            for division in divisions:
                chart_accounts = CTBDefault.get_all_div_accounts(division, base)
                for account in chart_accounts:
                    account_spec["accounts"].append(account)
                    CTBDefault.child_accounts.clear()
                    # for postable only
                    if account.coa_control == "2":
                        amount1, amount2 = T10Abs10.coa_bal_by_rpt_type(
                            account.id,
                            instance.year,
                            instance.month,
                            instance.type_of_rpt,
                        )
                        amount_dict[account.id] = float(amount1) + float(amount2)
                    else:
                        CTBDefault.fetch_children([account], division)
                        amount = 0
                        for child_acc in CTBDefault.child_accounts:
                            amount1, amount2 = T10Abs10.coa_bal_by_rpt_type(
                                child_acc.id,
                                instance.year,
                                instance.month,
                                instance.type_of_rpt,
                            )
                            amount += float(amount1) + float(amount2)
                        amount_dict[account.id] = amount
            coa_accounts.append(account_spec)

        # calling function to generate xlsx file
        csv_data = CTBDefault.export_ctb_csv(
            instance.company,
            instance.type_of_rpt,
            instance.year,
            instance.month,
            divisions,
            coa_accounts,
            amount_dict,
            division_confg,
        )

        # pdf_data = CTBDefault.export_ctb_pdf()
        pdf_data = None

    elif instance.rpt_code == "CSF":
        name = "cash_flow_statement"
        cash_flows = T01Cfl10.objects.filter(parent=None)
        stmt_flows = []
        stmt_opening_balance = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
        }
        stmt_closing_balance = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
        }
        for flow in cash_flows:
            flow_obj = {"detail": flow, "balance": {}, "sub_flows": []}
            flow_balance = {
                0: 0,
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                7: 0,
                8: 0,
                9: 0,
                10: 0,
                11: 0,
            }
            cash_sub_flows = T01Cfl10.objects.filter(parent=flow.id)
            for sub_flow in cash_sub_flows:
                sub_flow_obj = {"detail": sub_flow, "balance": {}, "accounts": []}
                accounts = T01Coa10.objects.filter(cashflow_group=sub_flow.id)
                sub_flow_balance = {
                    0: 0,
                    1: 0,
                    2: 0,
                    3: 0,
                    4: 0,
                    5: 0,
                    6: 0,
                    7: 0,
                    8: 0,
                    9: 0,
                    10: 0,
                    11: 0,
                }
                for account in accounts:
                    account_balance = {}
                    month, year = instance.month - 1, instance.year
                    for index in range(-1, 12):
                        # for january month , need to change year
                        if month == 0:
                            year -= 1
                            month = 12
                        yr, mn = get_fin_period(
                            datetime(year, month, 1),
                            instance.division.company.finyear_begin,
                        )
                        coa_objs = T10Abs10.objects.filter(
                            coa_id__id=account.id, fin_year=yr
                        )
                        balance = 0
                        for coa_obj in coa_objs:
                            coa_obj = coa_obj.__dict__
                            balance += Decimal(coa_obj[f"coa_p{mn:02d}_actual"] or 0.00)
                        if index == -1:
                            stmt_opening_balance[index + 1] += balance
                        else:
                            account_balance[index] = balance
                            sub_flow_balance[index] += account_balance[index]
                            flow_balance[index] += account_balance[index]
                            stmt_closing_balance[index] += account_balance[index]
                        month += 1
                        if month == 13:
                            month = 1
                            year += 1
                    flow_acc_obj = {"detail": account, "balance": account_balance}
                    sub_flow_obj["accounts"].append(flow_acc_obj)
                sub_flow_obj["balance"] = sub_flow_balance
                flow_obj["sub_flows"].append(sub_flow_obj)
            flow_obj["balance"] = flow_balance
            stmt_flows.append(flow_obj)

        x = instance.month
        for index in range(0, 12):
            stmt_closing_balance[index] += stmt_opening_balance[index]
            if index != -1:
                stmt_opening_balance[index + 1] += stmt_closing_balance[index]
            x += 1
            if x == 13:
                x = 1

        CshFlowStmt.initPDF(
            T01Div10.get_div_comp(instance.division),
            instance.month,
            instance.year,
            stmt_opening_balance,
        )
        CshFlowStmt.render_stmt_items(stmt_flows, instance.month, instance.year)

        pdf_data = CshFlowStmt.export_cfs_pdf(
            cash_flows, instance.month, instance.year, stmt_closing_balance
        )

        csv_data = CshFlowStmt.export_cfs_csv()

    elif instance.rpt_code == "TBDT":
        # functionality for Trial Balance as of dates
        name = "trial_balance_asof_date"
        # fetch all accounts
        chart_accounts = TBDefault.get_all_accounts(instance.division)

        # retrieve figures for accounts
        debits_dict, credits_dict = {}, {}
        for account in chart_accounts:
            TBDefault.child_accounts.clear()
            # for postable only
            debits_dict[account.id], credits_dict[account.id] = 0, 0
            balance = T10Abs10.coa_opening_bal(
                account.id, instance.as_of_date, instance.division.currency.id
            )

            if balance > 0:
                debits_dict[account.id] = balance
            else:
                credits_dict[account.id] = abs(balance)

        # calling function to create Xlsx file
        csv_data = TBDefault.export_tb_csv(
            instance.division,
            debits=debits_dict,
            credits=credits_dict,
            as_of_date=instance.as_of_date,
        )

        # calling function to create PDF
        pdf_data = TBDefault.export_tb_pdf(
            T01Div10.get_div_comp(instance.division),
            debits=debits_dict,
            credits=credits_dict,
            as_of_date=instance.as_of_date,
        )

    elif instance.rpt_code == "BSDT":
        # balance sheet functionality
        name = "balance_sheet_asof_date"
        # initialising pdf generation
        BSGeneral.initiationPDF(
            T01Div10.get_div_comp(instance.division), as_of_date=instance.as_of_date
        )
        BSGeneral.initiationCSV(as_of_date=instance.as_of_date)

        # for managing figures
        amount_dict = {}
        # fetch all accounts
        account_types = ["Assets", "Equities", "Liabilities"]

        for type in account_types:
            chart_accounts = BSGeneral.get_accounts(instance.division, type)
            for account in chart_accounts:
                # for postable only
                amount = 0
                if account.coa_control == "2":
                    amount = T10Abs10.coa_opening_bal(
                        account.id, instance.as_of_date, instance.division.currency.id
                    )
                else:
                    BSGeneral.child_accounts.clear()
                    if type == "Equities":
                        BSGeneral.pre_transversal(
                            [account],
                            instance.division,
                            False,
                            BSGeneral.child_accounts,
                        )
                    else:
                        BSGeneral.pre_transversal(
                            [account], instance.division, True, BSGeneral.child_accounts
                        )
                    temp = 0
                    for child in BSGeneral.child_accounts:
                        temp = T10Abs10.coa_opening_bal(
                            child.id, instance.as_of_date, instance.division.currency.id
                        )
                        amount += float(temp)
                amount_dict[account.id] = float(amount)

                if type == "Liabilities" or type == "Equities":
                    if amount_dict[account.id] < 0:
                        amount_dict[account.id] *= -1

            BSGeneral.render_accounts(chart_accounts, amount_dict, instance.year, type)
            BSGeneral.render_csv_accounts(
                chart_accounts, amount_dict, instance.year, type
            )
            chart_accounts.clear()

        # calling function to create Xlsx file
        csv_data = BSGeneral.export_bs_csv(
            instance.division, instance.type_of_rpt, instance.year, instance.month
        )

        # calling function to create PDF
        pdf_data = BSGeneral.export_bs_pdf()

    elif instance.rpt_code == "PLDT":
        # Profit loss functionality
        name = "profit_loss_asof_date"
        # initialising pdf generation
        IEGeneral.initiationPDF(
            T01Div10.get_div_comp(instance.division), as_of_date=instance.as_of_date
        )
        IEGeneral.initiationCSV(as_of_date=instance.as_of_date)

        amount_dict = {}
        account_types = ["Income", "COGS", "Expense"]

        for type in account_types:
            chart_accounts = IEGeneral.get_accounts(instance.division, type)
            for account in chart_accounts:
                # for postable only
                amount = 0
                if account.coa_control == "2":
                    amount = T10Abs10.coa_opening_bal(
                        account.id, instance.as_of_date, instance.division.currency.id
                    )
                else:
                    IEGeneral.child_accounts.clear()
                    if type == "COGS":
                        IEGeneral.pre_transversal(
                            [account],
                            instance.division,
                            False,
                            IEGeneral.child_accounts,
                        )
                    else:
                        IEGeneral.pre_transversal(
                            [account], instance.division, True, IEGeneral.child_accounts
                        )

                    temp = 0
                    for child in IEGeneral.child_accounts:
                        temp = T10Abs10.coa_opening_bal(
                            account.id,
                            instance.as_of_date,
                            instance.division.currency.id,
                        )
                        amount += float(temp)

                amount_dict[account.id] = float(amount)

                if type == "Income":
                    if amount_dict[account.id] < 0:
                        amount_dict[account.id] *= -1

            IEGeneral.render_accounts(chart_accounts, amount_dict, instance.year, type)
            IEGeneral.render_csv_accounts(chart_accounts, amount_dict, type)

        # calling function to create Xlsx file
        csv_data = IEGeneral.export_ie_csv(
            instance.division, instance.type_of_rpt, instance.year, instance.month
        )
        # calling function to create PDF
        pdf_data = IEGeneral.export_ie_pdf()

    # to keep only one copy of every instance
    pdf_file_name = get_path(f"reports/{name}_{str(instance.id)}.pdf")
    csv_file_name = get_path(f"reports/{name}_{str(instance.id)}.xlsx")

    file_name_csv = None
    file_name_pdf = None

    if csv_data:
        if default_storage.exists(csv_file_name):
            default_storage.delete(csv_file_name)
        file_name_csv = default_storage.save(csv_file_name, csv_data)

    if pdf_data:
        if default_storage.exists(pdf_file_name):
            default_storage.delete(pdf_file_name)
        file_name_pdf = default_storage.save(pdf_file_name, pdf_data)

    return file_name_pdf, file_name_csv
