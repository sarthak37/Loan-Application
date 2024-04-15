# Generated by Django 4.2.11 on 2024-04-14 08:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_remove_loanapplication_loan_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanapplication',
            name='id',
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='loan_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]