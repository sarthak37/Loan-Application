from decimal import Decimal, ROUND_HALF_UP
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, LoanApplication, Payment
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, LoanApplicationSerializer, PaymentSerializer, ApplyLoanInputSerializer, MakePaymentInputSerializer
import csv
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from datetime import datetime,timedelta
from decimal import Decimal
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserSerializer
from drf_yasg import openapi





class UserAPIView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplyLoanAPIView(APIView):
    @swagger_auto_schema(
    request_body=ApplyLoanInputSerializer,
    responses={201: LoanApplicationSerializer}
)
    def post(self, request):
        user_id = request.data.get('unique_user_id')
        loan_type = request.data.get('loan_type')
        loan_amount = Decimal(request.data.get('loan_amount'))
        interest_rate = Decimal(request.data.get('interest_rate'))
        term_period = int(request.data.get('term_period'))
        disbursement_date = parse_date(request.data.get('disbursement_date'))

        try:
            # Open the CSV file
            with open('data.csv', mode='r') as file:
                # Create a CSV reader
                reader = csv.DictReader(file)
                
                # Convert CSV data to a list of dictionaries
                data = list(reader)
        except FileNotFoundError:
            return JsonResponse({'error': 'File not found.'}, status=404)
        except csv.Error as e:
            return JsonResponse({'error': 'Invalid CSV data.', 'details': str(e)}, status=400)

        # Calculate the total credit and debit amounts
        total_credit = sum(int(item['amount']) for item in data if item['transaction_type'] == 'CREDIT')
        total_debit = sum(int(item['amount']) for item in data if item['transaction_type'] == 'DEBIT')

        # Calculate the amount
        amt = total_credit - total_debit

        # Calculate the credit score
        if amt >= 1000000:
            credit_score = 900
        elif amt <= 100000:
            credit_score = 300
        else:
            credit_score = 300 + ((amt - 100000) // 15000) * 10

        if loan_type.lower() != 'credit card':
            return Response({'error': 'Unsupported loan type'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(unique_user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if  credit_score < 450 or user.annual_income < Decimal('150000'):
            return Response({'error': 'Loan application declined due to credit score or income'}, status=status.HTTP_400_BAD_REQUEST)

        if loan_amount > Decimal('5000'):
            return Response({'error': 'Loan amount exceeds limit'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the daily APR accrued
        daily_interest_rate = (interest_rate / Decimal('365')) / Decimal('100')

        # Calculate the monthly interest rate
        monthly_interest_rate = daily_interest_rate * Decimal('30')

        l = ((100 + interest_rate)/100) * loan_amount

        # Calculate the EMI using the amortization formula
        emi = (l / 12)
        emi = emi.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        # Check if EMI exceeds 20% of monthly income
        monthly_income = user.annual_income / 12
        if emi > (monthly_income * Decimal('0.20')):
            return Response({'error': 'EMI exceeds monthly income limit'}, status=status.HTTP_400_BAD_REQUEST)

        # Create loan application with EMI
        loan_application = LoanApplication(
            user=user,
            loan_type=loan_type,
            loan_amount=l,
            interest_rate=interest_rate,
            term_period=term_period,
            disbursement_date=disbursement_date,
            emi=emi  # Set the calculated EMI here
        )
        loan_application.save()  # Save the instance after setting all fields


        # Calculate due dates
        due_dates = loan_application.calculate_due_dates()

        # Prepare the response data
        response_data = {
            'Error': None,
            'Loan_id': str(loan_application.loan_id),
            'Due_dates': due_dates
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class MakePaymentAPIView(APIView):
    @swagger_auto_schema(
    request_body=MakePaymentInputSerializer,
    responses={200: openapi.Response('Payment Successful', PaymentSerializer)}
)

    def post(self, request):
        serializer = MakePaymentInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        loan_id = data['loan_id']
        amount = data['amount']
        payment_date = data['date_of_payment']

      

        loan = get_object_or_404(LoanApplication, loan_id=loan_id)
        total_paid = loan.payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')

        # Calculate the remaining amount before making the new payment
        amount_remaining_before_payment = loan.loan_amount - total_paid

        # Check if payment is already made for the current month and year
        payments_this_month = loan.payments.filter(date_of_last_payment__year=payment_date.year,
                                                   date_of_last_payment__month=payment_date.month)
        if payments_this_month.exists():
            return Response({'error': 'Payment already made for this month'}, status=status.HTTP_400_BAD_REQUEST)
        # Check if there is a previous unpaid EMI
        last_payment = loan.payments.last()
        if last_payment and (payment_date.month - last_payment.date_of_last_payment.month > 1):
            return Response({'error': 'Previous EMI unpaid'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the payment amount is greater than the remaining amount
        if amount > amount_remaining_before_payment:
            return Response({'error': 'Amount is more than remaining balance'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the new remaining amount after the payment
        amount_remaining_after_payment = amount_remaining_before_payment - amount

        # Check if the loan is already paid off
        if amount_remaining_after_payment <= 0:
            return Response({'error': 'Loan is paid'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new payment record
        payment = Payment(
            loan=loan,
            amount_paid=amount,
            amount_remaining=amount_remaining_after_payment,
            date_of_last_payment=payment_date
        )
        payment.save()

        # Update the loan application with the new payment details
        loan.loan_amount -= amount
        loan.save(update_fields=['loan_amount'])

        return Response({'message': 'Amount paid successfully'}, status=status.HTTP_200_OK)

class LoanStatusAPIView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(LoanApplication, loan_id=loan_id)
        payments = loan.payments.all()

        total_amount_paid = sum(payment.amount_paid for payment in payments)
        amount_remaining = loan.loan_amount
        num_emis_paid = payments.count()
        new_term_period = loan.term_period - num_emis_paid

        daily_interest_rate = (loan.interest_rate / Decimal('365')) / Decimal('100')
        monthly_interest_rate = daily_interest_rate * Decimal('30')
        new_emi = amount_remaining * (monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** (-new_term_period)))
        new_emi = new_emi.quantize(Decimal('.01'), rounding=ROUND_HALF_UP) if new_term_period > 0 else Decimal('0.00')

        due_dates = loan.calculate_due_dates(new_emi)[num_emis_paid:]

        response_data = {
            'amount_paid': total_amount_paid,
            'amount_remaining': amount_remaining,
            'new_emi': new_emi,
            'due_dates': due_dates
        }

        return Response(response_data, status=status.HTTP_200_OK)

class LoanPaymentView(View):
    def get(self, request):
        # Extract the date parameter from the request
        date_param = request.GET.get('date', None)
        
        # Convert the date parameter to a datetime object
        try:
            date_object = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD format.'}, status=400)
        
        # Calculate the start and end of the previous month
        start_previous_month = date_object.replace(day=1) - relativedelta(months=1)
        end_previous_month = date_object.replace(day=1) - timedelta(days=1)
        
        # Find payments for the previous month
        payments_previous_month = Payment.objects.filter(
            date_of_last_payment__gte=start_previous_month,
            date_of_last_payment__lte=end_previous_month
        )
        
        # Find payments for the current month
        payments_current_month = Payment.objects.filter(
            date_of_last_payment__gte=date_object.replace(day=1)
        )
        
        # Get the user IDs for payments made in the previous month
        user_ids_previous_month = set(payment.loan.user.id for payment in payments_previous_month)
        
        # Get the user IDs for payments made in the current month
        user_ids_current_month = set(payment.loan.user.id for payment in payments_current_month)
        
        # Exclude user IDs that have made a payment in the current month
        user_ids = list(user_ids_previous_month - user_ids_current_month)
        
        # Return the user IDs as a response
        return JsonResponse({'user_ids': user_ids})
