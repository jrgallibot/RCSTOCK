from django.db import models
from django.utils import timezone

from app.models import AuthUser


class TblFaq(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    isactive = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_faq'


class TblPriceDevelopment(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_price_development'


class TblSubPriceDevelopment(models.Model):
    id = models.BigAutoField(primary_key=True)
    prod = models.ForeignKey(TblPriceDevelopment, models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_sub_price_development'


class TblMembershipPricing(models.Model):
    id = models.BigAutoField(primary_key=True)
    membership_type = models.CharField(max_length=255, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    services = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tbl_membership_pricing'


class TblSubscription(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    membership = models.ForeignKey(TblMembershipPricing, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    invoice = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_subscription'


class TblGeneralInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    system_name = models.CharField(max_length=255, blank=True, null=True)
    system_version = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    mobile_no = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    tel_no = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    picture = models.FileField(upload_to='rcstockv_logo/')
    about = models.TextField(blank=True, null=True)
    data_protection = models.TextField(blank=True, null=True)
    affiliate = models.TextField(blank=True, null=True)
    market_intelligence = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    updatedby = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        db_table = 'tbl_general_info'


class Loghistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    descriptions = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    datetime_added = models.DateTimeField(blank=True, null=True, default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_loghistory'


class Supplier(models.Model):
    id = models.IntegerField(primary_key=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    home_page = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    date_create = models.DateTimeField(blank=True, null=True, default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_supplier'

class TblContactUs(models.Model):
    id = models.BigAutoField(primary_key=True)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    is_seen = models.SmallIntegerField(blank=True, null=True)
    is_reply = models.SmallIntegerField(blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True, default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_contact_us'

class TblContactUsReply(models.Model):
    id = models.BigAutoField(primary_key=True)
    query = models.ForeignKey(TblContactUs, models.DO_NOTHING)
    replied_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    message = models.TextField(blank=True, null=True)
    datetime_added = models.DateTimeField(blank=True, null=True, default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_contact_us_reply'