from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException


class ExistEmailException(APIException):
    status_code = 400
    default_detail = _("This Email already exists. Please enter a new email.")
    default_code = "exist-email"


class ExistUsernameException(APIException):
    status_code = 400
    default_detail = _("This Username already exists. Please enter a new username.")
    default_code = "exist-username"


class AccountDisabledException(APIException):
    status_code = 403
    default_detail = _("User account is disabled.")
    default_code = "account-disabled"


class InvalidCredentialsException(APIException):
    status_code = 401
    default_detail = _("Wrong username or password.")
    default_code = "invalid-credentials"


class SendingOTPException(APIException):
    status_code = 500
    default_detail = _("Something went wrong to send otp.")
    default_code = "send-otp-error"


class ExpiredOtpException(APIException):
    status_code = 408
    default_detail = _("Given otp is expired!!")
    default_code = "time-out"


class InvalidOtpException(APIException):
    status_code = 400
    default_detail = _("Invalid otp OR No any active user found for given otp")
    default_code = "invalid-otp"


class LockFlagException(APIException):
    status_code = 423
    default_detail = _("Locked data cannot edit or delete.")
    default_code = "locked_error"


class PostFlagException(APIException):
    status_code = 423
    default_detail = _("Posted data cannot delete.")
    default_code = "server_error"


class ProtectedErrorException(APIException):
    status_code = 400
    default_detail = _("Cannot delete as it is related with others.")
    default_code = "server_error"
