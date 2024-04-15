from rest_framework import serializers
from .models import User, LoanApplication, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['aadhar_id', 'name', 'email_id', 'annual_income', 'unique_user_id']

class LoanApplicationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = LoanApplication
        fields = ['user', 'loan_type', 'loan_amount', 'interest_rate', 'term_period', 'disbursement_date', 'emi', 'loan_id'] 

        read_only_fields = ['emi']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['Due_dates'] = instance.calculate_due_dates()
        return representation         

class PaymentSerializer(serializers.ModelSerializer):
    loan = serializers.SlugRelatedField(slug_field='loan_id', queryset=LoanApplication.objects.all())

    class Meta:
        model = Payment
        fields = ['payment_id', 'loan', 'amount_paid', 'amount_remaining', 'date_of_last_payment']

    def validate(self, data):
        """
        Check that the payment amount is not greater than the remaining loan amount.
        """
        loan = data['loan']
        amount_paid = data['amount_paid']
        total_paid = sum(loan.payments.values_list('amount_paid', flat=True))
        amount_remaining = loan.loan_amount - total_paid

        if amount_paid > amount_remaining:
            raise serializers.ValidationError("Amount is more than remaining balance")
        return data

    def create(self, validated_data):
        """
        Create and return a new `Payment` instance, given the validated data.
        """
        # Additional logic to handle payment creation can be added here
        return Payment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Payment` instance, given the validated data.
        """
        # Additional logic to handle payment update can be added here
        instance.amount_paid = validated_data.get('amount_paid', instance.amount_paid)
        instance.amount_remaining = validated_data.get('amount_remaining', instance.amount_remaining)
        instance.date_of_last_payment = validated_data.get('date_of_last_payment', instance.date_of_last_payment)
        instance.save()
        return instance      
