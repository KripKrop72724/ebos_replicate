import calendar
import io
import os

from django.conf import settings
from django.core.files.storage import default_storage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5, inch, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from ebos2206.models.m06_att_trn import T06Prs10
from ebos2206.models.m06_emp_mas import T06Emp15
from ebos2206.models.m06_prl_trn import T06Prl10, T06Prl15
from ebos2201.utils import get_path

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


class PrintPrlCk:
    def __init__(self, ins: object) -> None:
        self.instance = ins
        self.render()

    def myFirstPage(self, canvas, doc):
        canvas.saveState()
        canvas.setLineWidth(5)
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(40, 560, self.instance.division.company.company_name)
        canvas.setFont("Helvetica", 11)
        canvas.drawString(40, 540, self.instance.division.company.company_location)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(
            300,
            540,
            f"{MONTH_NAMES[self.instance.pay_month-1]} {self.instance.pay_year} Payroll CheckList",
        )
        # canvas.drawString(640, 540, f"Total No. of Pages : {self.total_pages}")
        canvas.drawString(10.5 * inch, 0.75 * inch, f"Page {doc.page}")
        canvas.restoreState()

    def myLaterPages(self, canvas, doc):
        canvas.saveState()
        canvas.drawString(10.5 * inch, 0.75 * inch, "Page %d" % doc.page)
        canvas.restoreState()

    def render(self):
        table_data = [
            [
                "#",
                "Employee Name \n Code  Designation",
                "DP ML EL \n LOP AB SC",
                "Basic OT Pay ML Pay",
                "Job Attendance \n Job No.  Days OT hrs.",
                "Allowance \n Desc Amount",
                "(Other) Deductions \n Desc  Amount",
                "Loan Deductions \n Desc  Amount",
            ]
        ]
        
        folder = get_path("payroll_reports")

        # checking if the directory payroll_reports exist or not.
        if not os.path.isdir(f"{settings.MEDIA_ROOT}/{folder}"):
            # if the payroll_reports directory is not present then create it.
            os.makedirs(f"{settings.MEDIA_ROOT}/{folder}")

        file_name_pdf = f"{folder}/report_{self.instance.id}.pdf"
        file_path = os.path.join(str(settings.MEDIA_ROOT), file_name_pdf)

        # Existing file remove
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        doc = SimpleDocTemplate(file_path, pagesize=(landscape(A4)))

        for index, T06Prl10_record in enumerate(self.instance.payroll_set.all()):
            self.per_page_row = index + 1
            total_allowance = int(T06Prl10_record.fixed_alw or 0) + int(
                T06Prl10_record.variable_alw or 0
            )
            T06Prl15_loan_deduction = T06Prl15.objects.filter(
                payroll_id=T06Prl10_record.id
            ).first()
            other_deductions = (
                T06Prl10_record.deductions if T06Prl10_record.deductions else ""
            )
            loan_deduction = (
                T06Prl15_loan_deduction.loan_deduction
                if T06Prl15_loan_deduction
                else ""
            )
            Employee_Name = (
                str(T06Prl10_record.employee_code.first_name)
                + " "
                + str(T06Prl10_record.employee_code.last_name)
            )
            data_list = [
                index + 1,
                ""
                + Employee_Name
                + "\n"
                + str(T06Prl10_record.employee_code.employee_code)
                + " "
                + T06Prl10_record.employee_code.designation.designation if T06Prl10_record.employee_code.designation else "",
                ""
                + str(T06Prl10_record.tot_days_worked)
                + " "
                + str(T06Prl10_record.tot_ML_days)
                + " "
                + str(T06Prl10_record.tot_EL_days)
                + "\n"
                + " "
                + str(T06Prl10_record.tot_LOP_days)
                + " "
                + str(T06Prl10_record.tot_ABS_days)
                + " "
                + str(T06Prl10_record.tot_SubCont_days),
                ""
                + str(T06Prl10_record.basic_pay)
                + " "
                + str(T06Prl10_record.ot_pay)
                + " "
                + str(T06Prl10_record.ml_pay),
                "" + "Job No." + " " + "Days" + " " + str(T06Prl10_record.tot_ot_hours),
                "" + "Desc" + " " + str(total_allowance),
                "" + "Desc" + " " + str(other_deductions),
                "" + "Desc" + " " + str(loan_deduction),
            ]
            table_data.append(data_list)

        f = Table(table_data, repeatRows=1)
        f.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        f._argW[3] = 3.0 * inch
        elements = []
        elements.append(f)

        doc.build(
            elements, onFirstPage=self.myFirstPage, onLaterPages=self.myLaterPages
        )
        self.total_pages = doc.page

        prs_obj = T06Prs10.objects.filter(id=self.instance.id).update(
            payroll_checklist=file_name_pdf
        )

        return prs_obj


class PrintPSlip:
    def __init__(self, ins: object, employee_code: int = None) -> None:
        self.instance = ins
        self.employee_code = employee_code
        self.render()

    def render(self):
        T06Prl10_queryset = T06Prl10.objects.filter(payroll_period=self.instance.id)
        file_name = get_path("payslips/payslip.pdf")

        if self.employee_code:
            T06Prl10_queryset = T06Prl10_queryset.filter(
                employee_code__employee_code=self.employee_code
            )
            file_name = get_path(f"payslips/payslip_{self.employee_code}.pdf")
            file_path = os.path.join(str(settings.MEDIA_ROOT), file_name)

            # Existing file remove
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

        buffer = io.BytesIO()
        fileobj = canvas.Canvas(buffer, pagesize=(landscape(A5)))
        for T06Prl10_record in T06Prl10_queryset:
            Employee_Name = (
                str(T06Prl10_record.employee_code.first_name)
                + " "
                + str(T06Prl10_record.employee_code.last_name)
            )
            fileobj.setFont("Helvetica-Bold", 16)
            fileobj.drawString(40, 350, self.instance.division.company.company_name)
            fileobj.setFont("Helvetica", 11)
            fileobj.drawString(40, 330, self.instance.division.company.company_location)

            fileobj.line(40, 320, 560, 320)
            fileobj.drawString(
                40,
                300,
                "("
                + str(T06Prl10_record.employee_code.employee_code)
                + ") "
                + str(Employee_Name),
            )
            fileobj.drawString(
                480, 300, str(calendar.month_name[self.instance.pay_month])
            )
            fileobj.drawString(540, 300, str(self.instance.pay_year))

            fileobj.setFont("Helvetica", 11)
            fileobj.drawString(40, 260, "Days Worked")
            fileobj.drawString(120, 260, ":")
            fileobj.drawString(
                130,
                260,
                str(
                    T06Prl10_record.tot_days_worked
                    if T06Prl10_record.tot_days_worked
                    else 0
                ),
            )
            fileobj.drawString(40, 240, "ML Days")
            fileobj.drawString(120, 240, ":")
            fileobj.drawString(
                130,
                240,
                str(T06Prl10_record.tot_ML_days if T06Prl10_record.tot_ML_days else 0),
            )
            fileobj.drawString(40, 220, "El Days")
            fileobj.drawString(120, 220, ":")
            fileobj.drawString(
                130,
                220,
                str(T06Prl10_record.tot_EL_days if T06Prl10_record.tot_EL_days else 0),
            )
            fileobj.drawString(40, 200, "LOP Days")
            fileobj.drawString(120, 200, ":")
            fileobj.drawString(
                130,
                200,
                str(
                    T06Prl10_record.tot_LOP_days if T06Prl10_record.tot_LOP_days else 0
                ),
            )
            fileobj.drawString(40, 180, "ABS Days")
            fileobj.drawString(120, 180, ":")
            fileobj.drawString(
                130,
                180,
                str(
                    T06Prl10_record.tot_ABS_days if T06Prl10_record.tot_ABS_days else 0
                ),
            )
            fileobj.drawString(40, 160, "SC Days")
            fileobj.drawString(120, 160, ":")
            fileobj.drawString(
                130,
                160,
                str(
                    T06Prl10_record.tot_SubCont_days
                    if T06Prl10_record.tot_SubCont_days
                    else 0
                ),
            )
            fileobj.drawString(40, 140, "OT Hrs.")
            fileobj.drawString(120, 140, ":")
            fileobj.drawString(
                130,
                140,
                str(
                    T06Prl10_record.tot_ot_hours if T06Prl10_record.tot_ot_hours else 0
                ),
            )

            fileobj.drawString(210, 260, "Basic Pay")
            fileobj.drawString(300, 260, ":")
            fileobj.drawString(
                310,
                260,
                str(T06Prl10_record.basic_pay if T06Prl10_record.basic_pay else 0),
            )
            fileobj.drawString(210, 240, "OT Pay")
            fileobj.drawString(300, 240, ":")
            fileobj.drawString(
                310, 240, str(T06Prl10_record.ot_pay if T06Prl10_record.ot_pay else 0)
            )
            fileobj.drawString(210, 220, "ML Pay")
            fileobj.drawString(300, 220, ":")
            fileobj.drawString(
                310, 220, str(T06Prl10_record.ml_pay if T06Prl10_record.ml_pay else 0)
            )
            fileobj.drawString(210, 200, "EL Pay")
            fileobj.drawString(300, 200, ":")
            fileobj.drawString(
                310, 200, str(T06Prl10_record.el_pay if T06Prl10_record.el_pay else 0)
            )
            fileobj.drawString(210, 180, "Other Pay")
            fileobj.drawString(300, 180, ":")
            fileobj.drawString(
                310,
                180,
                str(T06Prl10_record.other_pay if T06Prl10_record.other_pay else 0),
            )
            fileobj.drawString(210, 160, "Ticket Pay")
            fileobj.drawString(300, 160, ":")
            fileobj.drawString(
                310, 160, str(T06Prl10_record.tkt_pay if T06Prl10_record.tkt_pay else 0)
            )
            fileobj.drawString(210, 140, "Fixed Allw")
            fileobj.drawString(300, 140, ":")
            fileobj.drawString(
                310,
                140,
                str(T06Prl10_record.fixed_alw if T06Prl10_record.fixed_alw else 0),
            )
            fileobj.drawString(210, 120, "Variable Allw")
            fileobj.drawString(300, 120, ":")
            fileobj.drawString(
                310,
                120,
                str(T06Prl10_record.variable_alw if T06Prl10_record.fixed_alw else 0),
            )

            get_T06Emp15 = T06Emp15.objects.filter(
                employee_code=T06Prl10_record.employee_code.id
            ).first()
            loan_amount = get_T06Emp15.loan_amount if get_T06Emp15 else 0
            net_loan_balance = get_T06Emp15.net_loan_balance if get_T06Emp15 else 0
            total_loan_deduction = (
                get_T06Emp15.total_loan_deduction if get_T06Emp15 else 0
            )
            fileobj.drawString(380, 260, "Loan Amount")
            fileobj.drawString(500, 260, ":")
            fileobj.drawString(510, 260, str(loan_amount))
            fileobj.drawString(380, 240, "Loan Balance")
            fileobj.drawString(500, 240, ":")
            fileobj.drawString(510, 240, str(net_loan_balance))
            fileobj.drawString(380, 220, "Loan EMI")
            fileobj.drawString(500, 220, ":")
            fileobj.drawString(510, 220, str(T06Prl10_record.loan_emi))
            fileobj.drawString(380, 200, "Round Off")
            fileobj.drawString(500, 200, ":")
            fileobj.drawString(510, 200, str(T06Prl10_record.round_off))
            fileobj.drawString(380, 180, "Total Loan Deduction")
            fileobj.drawString(500, 180, ":")
            fileobj.drawString(510, 180, str(total_loan_deduction))
            fileobj.drawString(380, 160, "Deductions")
            fileobj.drawString(500, 160, ":")
            fileobj.drawString(510, 160, str(T06Prl10_record.deductions))

            net_amount = (
                (T06Prl10_record.basic_pay if T06Prl10_record.basic_pay else 0)
                + (T06Prl10_record.ot_pay if T06Prl10_record.ot_pay else 0)
                + (T06Prl10_record.ml_pay if T06Prl10_record.ml_pay else 0)
                + (T06Prl10_record.el_pay if T06Prl10_record.el_pay else 0)
                + (T06Prl10_record.other_pay if T06Prl10_record.other_pay else 0)
                + (T06Prl10_record.tkt_pay if T06Prl10_record.tkt_pay else 0)
                + (T06Prl10_record.fixed_alw if T06Prl10_record.fixed_alw else 0)
                + (T06Prl10_record.variable_alw if T06Prl10_record.variable_alw else 0)
            )
            fileobj.setFont("Helvetica-Bold", 11)
            fileobj.drawString(440, 80, "Net Amount : " + str(net_amount))
            fileobj.showPage()

        fileobj.save()
        buffer.seek(0)
        file_name_pdf = default_storage.save(f"{file_name}", buffer)

        if not self.employee_code:
            T06Prs10.objects.filter(id=self.instance.id).update(payslip=file_name_pdf)

        return file_name
