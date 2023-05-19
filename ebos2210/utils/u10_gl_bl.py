from datetime import date
from django.core.files.storage import default_storage
from django.db.models import Q, Sum

from ebos2201.models.m01_core_mas import *
from ebos2201.models.m01_fin_mas import *
from ebos2210.models.m10_fin_link import T10Abs10, T10Gld10, T10Gld11, T10Sbs10
from ebos2210.utils.u10_rpt_handler import RPTHandler
from ebos2210.views.v10_aging_report import AgingReport
from ebos2210.views.v10_chart_account_summary import ChartAccountSummary
from ebos2210.views.v10_day_book import DayOfBook
from ebos2210.views.v10_gl_contra_bal import GLCBalance
from ebos2210.views.v10_ledger_account_summary import LedgerAccountSummary
from ebos2210.views.v10_stmt_acc import StmtAccount
from ebos2210.views.v10_subledger_detail import SubledgerDetail
from ebos2201.utils import get_path

import logging
logging.getLogger('xhtml2pdf').propagate=False


def gl_balance(instance):
    # currency derived from division itself
    currency = RPTHandler.manageNestedValues(instance.division.currency, "id")

    if instance.rpt_code == "GLR":
        from ebos2210.views.v10_gl_running_bal import GLRBalance

        name = "gl_running_balance"
        voc_rows, op_bal = [], 0
        gld11_filters = {}
        if instance.coa != None:
            gld11_filters["vou_coa"] = instance.coa
            op_bal = T10Abs10.coa_opening_bal(
                instance.coa.id, instance.dt_from, currency
            )
        if instance.subledger != None:
            gld11_filters["vou_subledger"] = instance.subledger
            op_bal = T10Sbs10.sl_opening_bal(
                instance.subledger.id, instance.dt_from, currency
            )
        voc_rows = T10Gld11.objects.filter(
            vou_id__division=instance.division,
            vou_id__vou_date__range=[instance.dt_from, instance.dt_upto],
            vou_id__delete_flag=False,
            vou_id__post_flag=True,
            **gld11_filters
        ).exclude(vou_id__vou_type__voucher_type="YC").order_by(
            "vou_id__vou_date"
        )
    
        file_name_pdf = GLRBalance.export_glr_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.coa,
            instance.subledger,
            instance.dt_from,
            instance.dt_upto,
            op_bal,
            voc_rows,
            f"reports/{name}_{str(instance.id)}.pdf"
        )
        csv_data = GLRBalance.export_glr_csv(
            instance.coa,
            instance.subledger,
            instance.dt_from,
            instance.dt_upto,
            op_bal,
            voc_rows,
        )

    elif instance.rpt_code == "GLC":
        name = "gl_contra_balance"
        voc_rows, op_bal = [], 0
        gld11_filters = {}
        if instance.coa != None:
            gld11_filters["vou_coa"] = instance.coa
            op_bal = T10Abs10.coa_opening_bal(
                instance.coa.id, instance.dt_from, currency
            )
        if instance.subledger != None:
            gld11_filters["vou_subledger"] = instance.subledger
            op_bal = T10Sbs10.sl_opening_bal(
                instance.subledger.id, instance.dt_from, currency
            )

        voc_rows = T10Gld11.objects.filter(
            ~Q(**gld11_filters),
            vou_id__division=instance.division,
            vou_id__vou_date__range=[instance.dt_from, instance.dt_upto],
            vou_id__delete_flag=False,
            vou_id__post_flag=True,
        ).exclude(vou_id__vou_type__voucher_type="YC").order_by(
            "vou_id__vou_date"
        )

        file_name_pdf = GLCBalance.export_glc_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.coa,
            instance.subledger,
            instance.dt_from,
            instance.dt_upto,
            op_bal,
            voc_rows,
            f"reports/{name}_{str(instance.id)}.pdf"
        )

        csv_data = GLCBalance.export_glc_csv(
            instance.coa,
            instance.subledger,
            instance.dt_from,
            instance.dt_upto,
            op_bal,
            voc_rows,
        )

    elif instance.rpt_code == "SAO" or instance.rpt_code == "SAD":
        name = "stmt_of_accs"
        voc_rows, gld11_filters, op_bal = [], {}, 0

        if instance.subledger:
            gld11_filters["vou_subledger"] = instance.subledger
            op_bal = T10Sbs10.sl_opening_bal(
                instance.subledger.id, instance.dt_from, currency
            )

        voc_rows = T10Gld11.objects.filter(
            vou_id__division=instance.division,
            vou_id__vou_curr=instance.vou_curr,
            vou_id__vou_date__range=[instance.dt_from, instance.dt_upto],
            vou_id__delete_flag=False,
            vou_id__post_flag=True,
            **gld11_filters
        ).exclude(vou_id__vou_type__voucher_type="YC").order_by(
            "vou_id__vou_date"
        )

        file_name_pdf = StmtAccount.export_soa_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.subledger,
            instance.vou_curr,
            instance.rpt_code,
            instance.dt_from,
            instance.dt_upto,
            op_bal,
            voc_rows,
            f"reports/{name}_{str(instance.id)}.pdf"
        )
        
        csv_data = StmtAccount.export_soa_csv(
            instance.subledger,
            instance.vou_curr,
            instance.rpt_code,
            instance.dt_from,
            instance.dt_upto,
            0,
            voc_rows,
        )

    elif instance.rpt_code == "DBK":
        name = "day_of_book"
        count = 0
        DayOfBook.initiationPDF(
            T01Div10.get_div_comp(instance.division), instance.dt_from, instance.dt_upto
        )
        vouchers = T10Gld10.objects.filter(
            division=instance.division,
            vou_date__range=[instance.dt_from, instance.dt_upto],
            delete_flag=False,
            post_flag=True,
        ).order_by(
            "vou_date"
        )  # subledger=instance.subledger,
        for voucher in vouchers:
            voc_rows = T10Gld11.objects.filter(vou_id=voucher.id)
            DayOfBook.render_vouchers(voucher, voc_rows, count)
            count += 1

        voc_rows = T10Gld11.objects.filter(
            vou_id__division=instance.division,
            vou_id__vou_curr=instance.vou_curr,
            vou_id__vou_date__range=[instance.dt_from, instance.dt_upto],
            vou_id__delete_flag=False,
            vou_id__post_flag=True,
            **gld11_filters
        ).exclude(vou_id__vou_type__voucher_type="YC").order_by(
            "vou_id__vou_date"
        )

        file_name_pdf = DayOfBook.export_dbk_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.dt_from,
            instance.dt_upto,
            0,
            vouchers,
            f"reports/{name}_{str(instance.id)}.pdf"
        )

        csv_data = DayOfBook.export_dbk_csv(
            instance.dt_from, instance.dt_upto, 0, vouchers
        )

    elif instance.rpt_code == "SLD":
        name = "subledger_detail"
        gld11_filters = {}
        today = date.today()  # getting today as a current date
        if RPTHandler.check_if_last_day_of_month(instance.dt_upto) == False:
            upto_day = instance.dt_upto.day + 1
        else:
            upto_day = instance.dt_upto.day
        upto_date = date(instance.dt_upto.year, instance.dt_upto.month, upto_day)        
        
        if instance.coa != None:
            gld11_filters["vou_coa"] = instance.coa

        voc_rows = T10Gld11.objects.filter(
            vou_id__division=instance.division,
            vou_subledger__division=instance.division,
            vou_id__vou_date__range=[instance.dt_from, upto_date],
            vou_id__post_flag=True,
            **gld11_filters
        ).exclude(vou_id__vou_type__voucher_type="YC").order_by(
            "vou_id__vou_date"
        )

        # Get total debit credit
        subledgers = voc_rows.values("vou_subledger__subledger_no", "vou_subledger__subledger_name").\
            annotate(bcurr_debit_sum=Sum('bcurr_debit')).\
                annotate(bcurr_credit_sum=Sum('bcurr_credit'))
        
        # Get debit credit net balance
        subledgers = subledgers.annotate(amount=Sum('bcurr_debit') - Sum('bcurr_credit'))

        # Get grand total debit credit
        debit_total = voc_rows.aggregate(Sum("bcurr_debit"))['bcurr_debit__sum']
        credit_total = voc_rows.aggregate(Sum("bcurr_credit"))['bcurr_credit__sum']

        # Get grand net total debit credit balance
        # net_total = voc_rows.aggregate(net_balance=(Sum("bcurr_debit") - Sum("bcurr_credit")))['net_balance'] 
        net_debit_grand_total, net_credit_grand_total = 0, 0

        for subledger in subledgers:
            if subledger['amount'] > 0:
                net_debit_grand_total += subledger['amount']
            else:
                net_credit_grand_total += subledger['amount']

        data = {
            'company': T01Div10.get_div_comp(instance.division),
            'dt_from': instance.dt_from,
            'dt_to': instance.dt_upto,
            'coa': instance.coa,
            'subledgers': subledgers,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'net_debit_grand_total': net_debit_grand_total,
            'net_credit_grand_total': net_credit_grand_total,
            'file_name': f"reports/{name}_{str(instance.id)}.pdf"
        }

        file_name_pdf = SubledgerDetail.export_sub_pdf(**data)

        csv_data = SubledgerDetail.export_sub_csv(instance.dt_from)

    elif instance.rpt_code == "LEA":
        name = "ledger_account_summary"
        today = date.today()  # getting today as a current date
        
        if RPTHandler.check_if_last_day_of_month(instance.dt_upto) == False:
            upto_day = instance.dt_upto.day + 1
        else:
            upto_day = instance.dt_upto.day
        upto_date = date(instance.dt_upto.year, instance.dt_upto.month, upto_day)

        voc_rows, gld11_filters = [], {}

        if instance.subledger:
            gld11_filters["vou_subledger"] = instance.subledger

        voc_rows = T10Gld11.objects.filter(
            vou_id__division=instance.division,
            vou_id__post_flag=True,
            **gld11_filters
        ).exclude(vou_id__vou_type__voucher_type="YC").exclude(vou_id__vou_date__range=[upto_date, today])

        accounts = voc_rows.values("vou_coa__account_num", "vou_coa__account_name").\
            annotate(bcurr_debit_sum=Sum('bcurr_debit')).\
                annotate(bcurr_credit_sum=Sum('bcurr_credit'))

        debit_total = voc_rows.aggregate(Sum("bcurr_debit"))['bcurr_debit__sum']
        credit_total = voc_rows.aggregate(Sum("bcurr_credit"))['bcurr_credit__sum']       

        file_name_pdf = LedgerAccountSummary.export_ldg_acc_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.dt_upto,
            instance.subledger,
            accounts,
            debit_total,
            credit_total,
            f"reports/{name}_{str(instance.id)}.pdf"
        )

        csv_data = LedgerAccountSummary.export_ldg_acc_csv(instance.dt_upto)

    elif instance.rpt_code in ["CRA", "SLC"]:
        name = "chart_account_summary" if instance.rpt_code == "CRA" else "subledger_summary"
        gld11_filters = {}
        today = date.today()  # getting today as a current date
        if RPTHandler.check_if_last_day_of_month(instance.dt_upto) == False:
            upto_day = instance.dt_upto.day + 1
        else:
            upto_day = instance.dt_upto.day
        upto_date = date(instance.dt_upto.year, instance.dt_upto.month, upto_day)

        if instance.coa != None:
            gld11_filters["vou_coa"] = instance.coa

        voc_rows = T10Gld11.objects.filter(
            vou_id__division=instance.division,
            vou_id__post_flag=True,
            **gld11_filters
        ).exclude(vou_id__vou_type__voucher_type="YC").exclude(vou_id__vou_date__range=[upto_date, today])

        subledgers = voc_rows.values("vou_subledger__subledger_no", "vou_subledger__subledger_name", "vou_subledger__telephone1").\
            annotate(bcurr_debit_sum=Sum('bcurr_debit')).\
                annotate(bcurr_credit_sum=Sum('bcurr_credit'))

        debit_total = voc_rows.aggregate(Sum("bcurr_debit"))['bcurr_debit__sum']
        credit_total = voc_rows.aggregate(Sum("bcurr_credit"))['bcurr_credit__sum'] 

        file_name_pdf = ChartAccountSummary.export_chr_acc_pdf(
            instance.rpt_code,
            T01Div10.get_div_comp(instance.division),
            instance.dt_upto,
            instance.coa,
            subledgers,
            debit_total,
            credit_total,
            f"reports/{name}_{str(instance.id)}.pdf"
        )

        csv_data = ChartAccountSummary.export_chr_acc_csv(instance.dt_upto)

    elif instance.rpt_code == "AGR":
        name = "aging_report"
        today = date.today()  # getting today as a current date
        if RPTHandler.check_if_last_day_of_month(instance.dt_upto) == False:
            upto_day = instance.dt_upto.day + 1
        else:
            upto_day = instance.dt_upto.day
        upto_date = date(instance.dt_upto.year, instance.dt_upto.month, upto_day)
        gld11_filters = {}
        gld11_filters["vou_subledger"] = instance.subledger
        gld11_filters["vou_id__division"] = instance.division
        gld11_filters["vou_id__post_flag"] = True
        gl_vouchers = T10Gld11.objects.filter(**gld11_filters).exclude(
            vou_id__vou_date__range=[upto_date, today], vou_id__vou_type__voucher_type="YC")
        pdf_data = AgingReport.export_agr_pdf(
            T01Div10.get_div_comp(instance.division),
            instance.subledger,
            instance.dt_upto,
            instance.aging1,
            instance.aging2,
            instance.aging3,
            gl_vouchers,
        )
        csv_data = AgingReport.export_agr_csv(
            instance.subledger,
            instance.dt_upto,
            instance.aging1,
            instance.aging2,
            instance.aging3,
            gl_vouchers,
        )

    pdf_file_name = get_path(f"reports/{name}_{str(instance.id)}.pdf")
    csv_file_name = get_path(f"reports/{name}_{str(instance.id)}.xlsx")

    # if default_storage.exists(pdf_file_name):
    #     default_storage.delete(pdf_file_name)
    # file_name_pdf = default_storage.save(pdf_file_name, csv_data)
    
    if default_storage.exists(csv_file_name):
        default_storage.delete(csv_file_name)
    file_name_csv = default_storage.save(csv_file_name, csv_data)

    return file_name_pdf, file_name_csv
