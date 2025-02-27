# Generated by Django 3.2.7 on 2022-09-21 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20220918_2053'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchLogs',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('search_input', models.CharField(blank=True, max_length=100, null=True)),
                ('date_search', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tbl_search_logs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblMembershipPricing',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('membership_type', models.CharField(blank=True, max_length=255, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('services', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tbl_membership_pricing',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblSubscription',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('subscription_id', models.IntegerField(blank=True, null=True)),
                ('subscription_name', models.CharField(blank=True, max_length=255, null=True)),
                ('membership_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tbl_subscription',
                'managed': False,
            },
        ),
    ]
