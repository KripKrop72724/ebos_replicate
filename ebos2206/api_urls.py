from django.urls import include, path
from rest_framework_nested import routers

from ebos2206.views.v06_att_trn import (
    T06Ess01ViewSet,
    T06Ess05ViewSet,
    T06Ess06ViewSet,
    T06Lve10Viewset,
    T06Prs10ViewSet,
    T06Tam10ViewSet,
    T06Tbd10ViewSet,
    T06Tbm10ViewSet,
)
from ebos2206.views.v06_emp_mas import (
    T06Dex10Viewset, 
    T06Emp10ViewSet,
    T06Emp11ViewSet,
    T06Emp12ViewSet,
    T06Emp13ViewSet,
    T06Emp14ViewSet,
    T06Emp15ViewSet,
    T06Emp16ViewSet,
    T06Emp17ViewSet,
    T06Emp18ViewSet,
)
from ebos2206.views.v06_hr_mas import (
    T06Alw10ViewSet,
    T06Ded10ViewSet,
    T06Doc10ViewSet,
    T06Lon10ViewSet,
    T06Lvr10Viewset,
    T06Tkr10ViewSet,
)
from ebos2206.views.v06_hr_trn import (
    T06Eos10ViewSet,
    T06Ess02ViewSet,
    T06Ess03ViewSet,
    T06Ess04ViewSet,
    T06Exc10ViewSet,
    T06Hdt10ViewSet,
    T06Mem10ViewSet,
    T06Wps10ViewSet,
)
from ebos2206.views.v06_prl_trn import (
    T06Prl10ViewSet,
    T06Prl11ViewSet,
    T06Prl12ViewSet,
    T06Prl13ViewSet,
    T06Prl14ViewSet,
    T06Prl15ViewSet,
    T06Prl16ViewSet,
)

app_name = "ebos2206"

router = routers.SimpleRouter()

# Payroll master routers
router.register("allowance_master", T06Alw10ViewSet, basename="allowance_master")
router.register("deduction_type", T06Ded10ViewSet, basename="deduction_type")
router.register("document_type", T06Doc10ViewSet, basename="document_type")
router.register("loan_master", T06Lon10ViewSet, basename="loan_master")
router.register("air_ticket_rule", T06Tkr10ViewSet, basename="air_ticket_rule")
router.register("employee_memo", T06Mem10ViewSet, basename="employee_memo")
router.register("expanse_claim", T06Exc10ViewSet, basename="expanse_claim")
router.register("help_desk_ticket", T06Hdt10ViewSet, basename="help_desk_ticket")

# Payroll routers
router.register("run_setup", T06Prs10ViewSet, basename="payroll_run_setup")

# Attendance routers
machine_att_router = routers.NestedSimpleRouter(
    router, r"run_setup", lookup="payroll_period"
)
machine_att_router.register(
    r"machine_data", T06Tam10ViewSet, basename="attendance-machine"
)

daily_att_router = routers.NestedSimpleRouter(
    router, r"run_setup", lookup="payroll_period"
)
daily_att_router.register(
    r"daily_time_booking", T06Tbd10ViewSet, basename="attendance-daily"
)

monthly_att_router = routers.NestedSimpleRouter(
    router, r"run_setup", lookup="payroll_period"
)
monthly_att_router.register(
    r"monthly_time_booking", T06Tbm10ViewSet, basename="attendance-monthly_time_booking"
)

# Payroll summery routers
payroll_summery_router = routers.NestedSimpleRouter(
    router, r"run_setup", lookup="payroll_period"
)
payroll_summery_router.register(
    r"payroll_summery", T06Prl10ViewSet, basename="payroll-summery"
)

labour_cost_router = routers.NestedSimpleRouter(
    payroll_summery_router, r"payroll_summery", lookup="payroll_id"
)
labour_cost_router.register(r"labour_cost", T06Prl11ViewSet, basename="labour-cost")

leave_amount_router = routers.NestedSimpleRouter(
    payroll_summery_router, r"payroll_summery", lookup="payroll_id"
)
leave_amount_router.register(r"leave_amount", T06Prl12ViewSet, basename="leave_amount")

allowance_amount_router = routers.NestedSimpleRouter(
    payroll_summery_router, r"payroll_summery", lookup="payroll_id"
)
allowance_amount_router.register(
    r"allowance_amount", T06Prl13ViewSet, basename="allowance_amount"
)

ticket_amount_router = routers.NestedSimpleRouter(
    payroll_summery_router, r"payroll_summery", lookup="payroll_id"
)
ticket_amount_router.register(
    r"ticket_amount", T06Prl14ViewSet, basename="ticket_amount"
)

loan_emi_router = routers.NestedSimpleRouter(
    payroll_summery_router, r"payroll_summery", lookup="payroll_id"
)
loan_emi_router.register(r"loan_emi", T06Prl15ViewSet, basename="loan_emi")

deduction_amount_router = routers.NestedSimpleRouter(
    payroll_summery_router, r"payroll_summery", lookup="payroll_id"
)
deduction_amount_router.register(
    r"deduction_amount", T06Prl16ViewSet, basename="deduction_amount"
)

attendance_urlpatterns = [
    path("", include(machine_att_router.urls)),
    path("", include(daily_att_router.urls)),
    path("", include(monthly_att_router.urls)),
    path("", include(payroll_summery_router.urls)),
    path("", include(labour_cost_router.urls)),
    path("", include(leave_amount_router.urls)),
    path("", include(allowance_amount_router.urls)),
    path("", include(ticket_amount_router.urls)),
    path("", include(loan_emi_router.urls)),
    path("", include(deduction_amount_router.urls)),
]

# employee routers
router.register("employees", T06Emp10ViewSet, basename="employees")


bank_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
bank_router.register(r'bank_account', T06Emp11ViewSet, basename='employee-bank')

leave_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
leave_record_router.register(r'leave_record', T06Emp12ViewSet, basename='employee-leave_record')

allowance_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
allowance_record_router.register(r'allowance_record', T06Emp13ViewSet, basename='employee-allowance_record')

ticket_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
ticket_record_router.register(r'ticket_record', T06Emp14ViewSet, basename='employee-ticket_record')

loan_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
loan_record_router.register(r'loan_record', T06Emp15ViewSet, basename='employee-loan_record')

deduction_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
deduction_record_router.register(r'deduction_record', T06Emp16ViewSet, basename='employee-deduction_record')

asset_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
asset_record_router.register(r'asset_record', T06Emp17ViewSet, basename='employee-asset_record')

document_record_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
document_record_router.register(r'document_record', T06Emp18ViewSet, basename='employee-document_record')

# HR transaction routes & reports
router.register("wps_files", T06Wps10ViewSet, basename="wps_files")
router.register("end_of_service", T06Eos10ViewSet, basename="end_of_service")
router.register(
    "document_expiry_report", T06Dex10Viewset, basename="document-expiry-report"
)

# Leave routers
router.register("leave_rules", T06Lvr10Viewset, basename="leave-rules")
router.register("leave_application", T06Lve10Viewset, basename="leave-application")


# Employee self service
router.register(
    "self_leave_application", T06Ess01ViewSet, basename="self_service_leave_application"
)
router.register(
    "self_expense_claim", T06Ess02ViewSet, basename="self_service_expense_claim"
)
router.register("self_help_desk", T06Ess03ViewSet, basename="self_service_help_desk")
router.register(
    "self_service_memo", T06Ess04ViewSet, basename="self_service_service_memo"
)
router.register("self_payslip", T06Ess05ViewSet, basename="self_service_payslip")
router.register(
    "self_monthly_timesheet", T06Ess06ViewSet, basename="self_service_monthly_timesheet"
)

employee_urlpatterns = [
    path('', include(bank_router.urls)),
    path('', include(leave_record_router.urls)),
    path('', include(allowance_record_router.urls)),
    path('', include(ticket_record_router.urls)),
    path('', include(loan_record_router.urls)),
    path('', include(deduction_record_router.urls)),
    path('', include(asset_record_router.urls)),
    path('', include(document_record_router.urls)),
]

urlpatterns = [
    path("", include(router.urls)),
] + attendance_urlpatterns + employee_urlpatterns
