from django.contrib import admin

from django.contrib import admin
from .models import User, LoanApplication, Payment

admin.site.register(User)
admin.site.register(LoanApplication)
admin.site.register(Payment)

