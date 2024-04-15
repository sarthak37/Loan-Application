from django.urls import path
from .views import UserAPIView, ApplyLoanAPIView, MakePaymentAPIView,LoanStatusAPIView, LoanPaymentView


urlpatterns = [
    path('api/user/', UserAPIView.as_view()),
    path('api/apply-loan/', ApplyLoanAPIView.as_view(), name='apply-loan-api'),
    path('api/make_payment/', MakePaymentAPIView.as_view(), name='make_payment'),
    path('api/loan_status/<loan_id>/', LoanStatusAPIView.as_view(), name='loan_status'),
    path('api/loan-payments/', LoanPaymentView.as_view(), name='loan-payments'),
]
