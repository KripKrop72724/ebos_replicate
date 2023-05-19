from django.urls import path

from ebos2201.views.v01_autocomplete import (
    ActivityGroupAutocomplete,
    CashflowGroupAutocomplete,
    DivisionAutocomplete,
    ParentCoaAutocomplete,
    SldAutocomplete,
    SubledgerTypeAutocomplete,
)

app_name = "ebos2201"

urlpatterns = [
    path(
        "division-autocomplete/",
        DivisionAutocomplete.as_view(),
        name="division-autocomplete",
    ),
    path(
        "parent_coa-autocomplete/",
        ParentCoaAutocomplete.as_view(),
        name="parent_coa-autocomplete",
    ),
    path(
        "activity_group-autocomplete/",
        ActivityGroupAutocomplete.as_view(),
        name="activity_group-autocomplete",
    ),
    path(
        "cashflow_group-autocomplete/",
        CashflowGroupAutocomplete.as_view(),
        name="cashflow_group-autocomplete",
    ),
    path(
        "subledger_type-autocomplete/",
        SubledgerTypeAutocomplete.as_view(),
        name="subledger_type-autocomplete",
    ),
    path(
        "subledger-autocomplete/",
        SldAutocomplete.as_view(),
        name="subledger-autocomplete",
    ),
]
