from django.db import models
import uuid
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.models import User

class User(models.Model):
    aadhar_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    email_id = models.EmailField(unique=True)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    unique_user_id = models.UUIDField(default=uuid.uuid4, editable=False)

class LoanApplication(models.Model):
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    loan_type = models.CharField(max_length=100)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_period = models.IntegerField()
    disbursement_date = models.DateField()
    emi = models.DecimalField(max_digits=10, decimal_places=2)
    

    def calculate_due_dates(self, new_emi=None):
        due_dates = []
        billing_date = self.disbursement_date
        remaining_balance = self.loan_amount
        emi_to_use = new_emi if new_emi is not None else self.emi

        for _ in range(self.term_period):
            interest_for_month = remaining_balance * (self.interest_rate / Decimal('365') / Decimal('100')) * Decimal('30')
            principal_component = emi_to_use - interest_for_month
            remaining_balance -= principal_component
            due_date = billing_date + timedelta(days=15)

            due_dates.append({
                'Date': due_date.strftime('%Y-%m-%d'),
                'Amount_due': emi_to_use.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            })
            billing_date += timedelta(days=30)

        return due_dates


class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_last_payment = models.DateField()

    def save(self, *args, **kwargs):
        # Check if the loan is already paid off
        if self.amount_remaining == 0:
            raise ValueError("Loan is paid")
        super().save(*args, **kwargs)        


    
