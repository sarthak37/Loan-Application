from django.urls import path
from .views import UserAPIView, ApplyLoanAPIView, MakePaymentAPIView,LoanStatusAPIView, LoanPaymentView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin


schema_view = get_schema_view(
   openapi.Info(
      title="Loan Application API",
      default_version='v1',
      description="API documentation for your loan system",
      contact=openapi.Contact(email="support@example.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('api/user/', UserAPIView.as_view()),
    path('admin/', admin.site.urls),
    path('api/apply-loan/', ApplyLoanAPIView.as_view(), name='apply-loan-api'),
    path('api/make_payment/', MakePaymentAPIView.as_view(), name='make_payment'),
    path('api/loan_status/<loan_id>/', LoanStatusAPIView.as_view(), name='loan_status'),
    path('api/loan-payments/', LoanPaymentView.as_view(), name='loan-payments'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
