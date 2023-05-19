from rest_framework.routers import DefaultRouter

from .views.api_views.v01_auth import AccessContentView

from ebos2201.views.api_views.v01_core_mas import (
    GroupsViewSet,
    PermissionsViewSet,
    T01Atm10ViewSet,
    T01Bnk10ViewSet,
    T01Cat10ViewSet,
    T01Com10ViewSet,
    T01Cur10ViewSet,
    T01Cur11ViewSet,
    T01Dep10ViewSet,
    T01Div10ViewSet,
    T01Dsg10ViewSet,
    T01Voc11ViewSet,
    UserViewSet,
)
from ebos2201.views.api_views.v01_fin_mas import (
    T01Act10ViewSet,
    T01Cfl10ViewSet,
    T01Coa10ViewSet,
    T01Prj10ViewSet,
    T01Sld10Viewset,
    T01Slt10Viewset,
)

app_name = "ebos2201"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"setup_auto_email", T01Atm10ViewSet, basename="setup_auto_email")
router.register(r"groups", GroupsViewSet, basename="groups")
router.register(r"permissions", PermissionsViewSet, basename="permissions")
router.register(r"company", T01Com10ViewSet, basename="company")
router.register(r"currency", T01Cur10ViewSet, basename="currency")
router.register(r"currency_rate", T01Cur11ViewSet, basename="currency_rate")
router.register(r"bank_account", T01Bnk10ViewSet, basename="bank_account")
router.register(r"division", T01Div10ViewSet, basename="division")
router.register(r"department", T01Dep10ViewSet, basename="department")
router.register(r"designation", T01Dsg10ViewSet, basename="designation")
router.register(r"project", T01Prj10ViewSet, basename="project")
router.register(r"subledger_type", T01Slt10Viewset, basename="subledger_type")
router.register(r"activity_setup", T01Act10ViewSet, basename="activity_setup")
router.register(r"cashflow_setup", T01Cfl10ViewSet, basename="cashflow_setup")
router.register(r"chart_of_account", T01Coa10ViewSet, basename="chart_of_account")
router.register(r"subledger", T01Sld10Viewset, basename="subledger")
router.register(r"voucher_type", T01Voc11ViewSet, basename="voucher_type")
router.register(r"category_master", T01Cat10ViewSet, basename="category_master")
router.register(r"access_content", AccessContentView, basename="access_content")

urlpatterns = []

urlpatterns += router.urls
