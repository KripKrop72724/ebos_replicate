from django.urls import path
from rest_framework.routers import DefaultRouter

from ebos2210.views.api_views.v10_fin_gl import (
    T10Alc10CrView,
    T10Alc10DBView,
    T10Alc10Viewset,
    T10Alc11Viewset,
    T10Alc12Viewset,
    T10Glr01ViewSet,
    T10Glr02ViewSet,
)
from ebos2210.views.api_views.v10_fin_link import (
    T10Gld10Viewset,
    T10Tax10ViewSet,
    T10Wor10Viewset,
)

app_name = "ebos2210"

router = DefaultRouter()
router.register(r"work_order", T10Wor10Viewset, basename="work_order")
router.register(r"tax_setup", T10Tax10ViewSet, basename="tax_setup")
router.register(r"voucher", T10Gld10Viewset, basename="gl_voucher")
router.register(r"allocation", T10Alc10Viewset, basename="gl_allocation")
router.register(r"allocation_debit", T10Alc11Viewset, basename="gl_allocation_debit")
router.register(r"allocation_credit", T10Alc12Viewset, basename="gl_allocation_credit")
router.register(r"reports", T10Glr01ViewSet, basename="reports")
router.register(r"statements", T10Glr02ViewSet, basename="statements")


urlpatterns = [
    path("allocation/debit/", T10Alc10DBView.as_view()),
    path("allocation/credit/", T10Alc10CrView.as_view()),
]

urlpatterns += router.urls
