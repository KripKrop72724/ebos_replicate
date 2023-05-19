from django.urls import path

from .views import *

app_name = "ebos2210"


urlpatterns = [
    path(
        "vou_id-autocomplete/", VouIdAutocomplete.as_view(), name="vou_id-autocomplete"
    ),
    path(
        "prepay_coa-autocomplete/",
        PrePayCoaAutocomplete.as_view(),
        name="prepay_coa-autocomplete",
    ),
    path(
        "postable_coa-autocomplete/",
        PostableCoaAutocomplete.as_view(),
        name="postable_coa-autocomplete",
    ),
    path(
        "vou_type-autocomplete/",
        VouTypeAutocomplete.as_view(),
        name="vou_type-autocomplete",
    ),
    path(
        "vou_coa-autocomplete/",
        GlVouCoaAutocomplete.as_view(),
        name="vou_coa-autocomplete",
    ),
    path(
        "vou_subledger-autocomplete/",
        GlVouSubledgerAutocomplete.as_view(),
        name="vou_subledger-autocomplete",
    ),
    path(
        "work_order-autocomplete/",
        GlWorkOrderAutocomplete.as_view(),
        name="work_order-autocomplete",
    ),
    path(
        "inv_type-autocomplete/",
        InvTypeAutocomplete.as_view(),
        name="inv_type-autocomplete",
    ),
    path(
        "invoice-autocomplete/",
        InvoiceAutocomplete.as_view(),
        name="invoice-autocomplete",
    ),
]
