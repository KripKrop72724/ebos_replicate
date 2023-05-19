import calendar
import csv
import datetime
import io
import os
from io import StringIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from ebos2206.models.m06_hr_trn import T06Wps11
from ebos2201.utils import get_path


class WPSExport:
    """
    Render csv or pdf files of T06Wps10
    """

    def wps_csv_data(self, obj: object):
        file_name = f"WPS_{obj.wps_year}_{obj.wps_month}_{obj.com_UID}.csv"

        response = StringIO()
        writer = csv.writer(response)

        # Details lines
        T06Wps11_records = T06Wps11.objects.filter(wps_header=obj.id)

        # Adding T06Wps11 record to csv
        writer.writerow(
            [
                "Record Type",
                "Employee Unique Id",
                "Employee Name",
                "Agent Id",
                "Employee Bank Account",
                "Pay Start Date",
                "Pay End Date",
                "Days in Period",
                "Income Fixed Component",
                "Income Variable Component",
                "Days on leave for period",
                "Housing Allowance",
                "Conveyance Allowance",
                "Medical Allowance",
                "Annual Passage Allowance",
                "Overtime Allowance",
                "Other Allowance",
                "Leave Encashment",
            ]
        )
        values_list = []
        for T06Wps11_record in T06Wps11_records:
            wps_agent_code = (
                obj.division.wps_bank_code.wps_agent_code if obj.division else ""
            )
            T06Prl10_pay_year = T06Wps11_record.emp_prl_id.payroll_period.pay_year
            T06Prl10_pay_month = T06Wps11_record.emp_prl_id.payroll_period.pay_month
            pay_start_date = datetime.date(T06Prl10_pay_year, T06Prl10_pay_month, 1)
            pay_end_date = pay_start_date.replace(
                day=calendar.monthrange(T06Prl10_pay_year, T06Prl10_pay_month)[1]
            )
            days_in_period = (pay_end_date - pay_start_date).days
            values = (
                T06Wps11_record.emp_record_type,
                T06Wps11_record.emp_UID,
                T06Wps11_record.emp_name,
                wps_agent_code,
                T06Wps11_record.emp_Bnk_acct,
                pay_start_date,
                pay_end_date,
                days_in_period,
                T06Wps11_record.sal_fixed_amt,
                T06Wps11_record.sal_Variable_amt,
                T06Wps11_record.emp_lve_days,
                T06Wps11_record.emp_housing_alw,
                T06Wps11_record.emp_transport_alw,
                T06Wps11_record.emp_medical_alw,
                T06Wps11_record.emp_tkt_amt,
                T06Wps11_record.emp_ot_amt,
                T06Wps11_record.emp_other_alw,
                T06Wps11_record.emp_lve_encashment,
            )
            values_list.append(values)
        for value in values_list:
            writer.writerow(value)

        # Header line
        # Adding T06Wps10 records to csv
        writer.writerow(
            [
                "Record Type",
                "MOL Company Number",
                "Bank Routing Code",
                "File Creation Date",
                "File Creation Time",
                "Salary Month",
                "EDR Count",
                "Total Salary",
                "Payment Currency",
                "Employer Reference",
            ]
        )
        header_list = []
        current_date = datetime.datetime.now()
        values = (
            obj.com_record_type,
            obj.com_UID,
            obj.com_bnk_routing_code,
            current_date.date(),
            current_date.time(),
            obj.wps_month,
            obj.sal_record_count,
            obj.tot_sal_amount,
            obj.pay_curr,
            obj.com_ref_note,
        )
        header_list.append(values)
        for h_list in header_list:
            writer.writerow(h_list)

        csv_file = ContentFile(response.getvalue().encode("utf-8"))
        obj.sif_file_name.save(file_name, csv_file)
        obj.file_creation_dt = current_date
        obj.save()

        return obj.sif_file_name


class EOSExport:
    """
    Render csv or pdf files of T06Eos10
    """

    def eos_pdf_data(self, obj: object):
        folder = get_path("EOS")

        # checking if the directory EOS exist or not.
        if not os.path.isdir(f"{settings.MEDIA_ROOT}/{folder}"):
            # if the EOS directory is not present then create it.
            os.makedirs(f"{settings.MEDIA_ROOT}/{folder}")

        file_name = f"EOS_{obj.gratuity_days}_{obj.employee_code.employee_code}.pdf"
        PDF_FILE_NAME = f"{folder}/{file_name}"
        file_path = os.path.join(str(settings.MEDIA_ROOT), PDF_FILE_NAME)

        # Existing file remove
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        # Get the data
        employee_name = obj.employee_code.first_name + " " + obj.employee_code.last_name
        date_of_cancel = (
            obj.employee_code.date_of_cancel.date()
            if obj.employee_code.date_of_cancel
            else ""
        )
        gratuity_days = int(obj.gratuity_days)
        gratuity_amount = obj.gratuity_amount
        el_days = int(obj.el_days)
        el_amount = obj.el_amount
        loan_balance_amount = obj.loan_balance_amount
        ticket_amount = obj.ticket_amount
        pending_pay = obj.pending_pay
        pending_deduction = obj.pending_deduction
        net_amount = (
            gratuity_amount
            + el_amount
            + loan_balance_amount
            + ticket_amount
            + pending_pay
            + pending_deduction
        )

        # Create PDF file
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=(landscape(A4)))

        # Start writing the PDF here
        p.drawString(50, 520, "END OF SERVICE SETTLEMENT")

        p.drawString(50, 470, "Employee name:")
        p.drawString(300, 470, "Date of Relieving:")
        p.drawString(420, 470, "Status")

        p.drawString(50, 450, employee_name)
        p.drawString(300, 450, str(date_of_cancel))
        p.drawString(420, 450, "Resigned")

        p.drawString(200, 400, "Days")
        p.drawString(250, 400, "Remark")
        p.drawString(510, 400, "Amount")

        p.drawString(50, 380, "Gratuity days")
        p.drawString(200, 380, str(gratuity_days))
        p.drawString(250, 380, "Gratuity Amount")
        p.drawString(510, 380, str(gratuity_amount))

        p.drawString(50, 360, "EL Days")
        p.drawString(200, 360, str(el_days))
        p.drawString(250, 360, "EL Amount")
        p.drawString(510, 360, str(el_amount))

        p.drawString(50, 340, "Loan balance amount")
        p.drawString(510, 340, str(loan_balance_amount))

        p.drawString(50, 320, "Ticket amount")
        p.drawString(510, 320, str(ticket_amount))

        p.drawString(50, 300, "Pending Payments")
        p.drawString(510, 300, str(pending_pay))

        p.drawString(50, 280, "Pending Deductions")
        p.drawString(510, 280, str(pending_deduction))

        p.drawString(380, 260, "Net Amount")
        p.drawString(510, 260, str(net_amount))

        p.showPage()
        p.save()

        file_name_pdf = default_storage.save(PDF_FILE_NAME, buffer)

        # Save the file name
        obj.print_EOS = file_name_pdf
        obj.save()

        return PDF_FILE_NAME
