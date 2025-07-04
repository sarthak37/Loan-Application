from decimal import Decimal, ROUND_HALF_UP
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, LoanApplication, Payment
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, LoanApplicationSerializer, PaymentSerializer
import csv
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from datetime import date

class Command(BaseCommand):
    help = 'Run the LoanPaymentView logic as a scheduled task'

    def handle(self, *args, **kwargs):
        # Get today's date
        today = timezone.now().date()
        
        # Calculate the date one month before today
        start_previous_month = today.replace(day=1) - relativedelta(months=1)
        end_previous_month = today.replace(day=1) - timedelta(days=1)
        
        # Find payments for the previous month
        payments_previous_month = Payment.objects.filter(
            date_of_last_payment__gte=start_previous_month,
            date_of_last_payment__lte=end_previous_month
        )
        
        # Find payments for the current month
        payments_current_month = Payment.objects.filter(
            date_of_last_payment__gte=today.replace(day=1)
        )
        
        # Get the user IDs for payments made in the previous month
        user_ids_previous_month = set(payment.loan.user.id for payment in payments_previous_month)
        
        # Get the user IDs for payments made in the current month
        user_ids_current_month = set(payment.loan.user.id for payment in payments_current_month)
        
        # Exclude user IDs that have made a payment in the current month
        user_ids = list(user_ids_previous_month - user_ids_current_month)
        
        # Print the user IDs to the console or handle them as needed
        self.stdout.write(self.style.SUCCESS(f'User IDs: {user_ids}'))