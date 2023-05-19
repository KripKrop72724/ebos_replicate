from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt import views as jwt_views

from ebos2201.utils import stripe_webhook
from ebos2201.views import v01_main
from ebos2201.views.api_views.v01_auth import (
    LoginAPIView,
    LogoutView,
    TwoStepVerificationAPIView,
)

BASE_URLPATTERNS = [
    path("admin/", admin.site.urls),
    path("", v01_main.index, name="index"),
    path("thankyou/", v01_main.sendemail, name="sendemail"),
    path("grappelli/", include("grappelli.urls")),
    path("verify/", v01_main.send_otp, name="send_otp"),
    path("verifying/", v01_main.verify_otp, name="verify_otp"),
    path("ebos2201/", include("ebos2201.urls", namespace="ebos2201")),
    path("ebos2210/", include("ebos2210.urls", namespace="ebos2210")),
    path("webhook/", stripe_webhook),
    path("dashboard/", include("ebos2240.urls")),
]

API_URLPATTERNS = [
    # APPs endpints
    path("master/", include("ebos2201.api_urls", namespace="master_apis")),
    path("payroll/", include("ebos2206.api_urls", namespace="payroll_apis")),
    path("finance/", include("ebos2210.api_urls", namespace="finance_apis")),
    # Login apis
    path("auth/login/", LoginAPIView.as_view(), name="user_login"),
    path(
        "auth/two_step_verification/",
        TwoStepVerificationAPIView.as_view(),
        name="otp_verification",
    ),
    path(
        "api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
]

urlpatterns = (
    BASE_URLPATTERNS
    + API_URLPATTERNS
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

# Schema URLs
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
