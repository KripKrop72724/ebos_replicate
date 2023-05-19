from django.contrib import admin, messages
from django.shortcuts import redirect
from models import *


class ExtractData(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        from .views.v15_extract_data import fileuploaded as fileupload

        response = fileupload(obj.attachment, obj.document_type)
        messages.success(request, "Records added successfully!")
        return redirect(response)


class T15Rpa01Admin(admin.ModelAdmin):
    list_display = (
        "policy_type",
        "document_type",
        "policy_number",
        "tcf_number",
        "name",
        "phone",
        "inception_date",
        "expiryDate",
        "vehicle",
        "reg_Number",
        "body_type",
        "manufacture_year",
        "sum_insured",
    )


class T15Rpa02Admin(admin.ModelAdmin):
    list_display = (
        "id_num",
        "name",
        "nationality",
        "sex",
        "date_of_birth",
        "expiry_date",
        "card_num",
    )


class T15Rpa03Admin(admin.ModelAdmin):
    list_display = (
        "traffic_plate",
        "place_of_issue",
        "plate_cls",
        "traffic_code",
        "owner",
        "reg_date",
        "ins_type",
        "expiry_date",
    )


class T15Rpa04Admin(admin.ModelAdmin):
    list_display = (
        "license",
        "name",
        "nationality",
        "date_of_birth",
        "issue_date",
        "expiry_date",
        "place_of_issue",
    )


admin.site.register(T15rpa_extract_data, ExtractData)
admin.site.register(T15rpa_policy_data, T15Rpa01Admin)
admin.site.register(T15rpa_eid_data, T15Rpa02Admin)
admin.site.register(T15rpa_vehreg_data, T15Rpa03Admin)
admin.site.register(T15rpa_drvlic_data, T15Rpa04Admin)
