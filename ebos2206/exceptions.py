from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException


class DataExistsException(APIException):
    status_code = 400
    default_detail = _("Attendance data already exists.")
    default_code = "data_exists"


class DataNotExistsException(APIException):
    status_code = 404
    default_detail = _("Attendance data not available for the selected period.")
    default_code = "data_not_exists"


class DataNotLockedException(APIException):
    status_code = 423
    default_detail = _("Attendance data should be locked for this period.")
    default_code = "attn_lock"


class PrsNotExistsException(APIException):
    status_code = 404
    default_detail = _("No peayroll setup exists for this period.")
    default_code = "prs_not_exists"


class PrlNotLockedException(APIException):
    status_code = 400
    default_detail = _("Payroll should be locked for this period.")
    default_code = "prl_lock"


class PrlExistsException(APIException):
    status_code = 400
    default_detail = _("Payroll already processed.")
    default_code = "prl_data_exists"


class NonDeleteLeaveException(APIException):
    status_code = 423
    default_detail = _("Approved or rejected leave cannot be delete.")
    default_code = "cannot_delete_lve"
