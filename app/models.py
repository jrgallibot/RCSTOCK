from django.db import models
from django.utils import timezone


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    address = models.CharField(max_length=150, blank=True, null=True)

    @property
    def get_fullname(self):
        return "{}{} {}".format(self.first_name.title(), " " + self.middle_name[:1] + "." if self.middle_name else '',
                                self.last_name.title())

    @property
    def get_fullname_formatted(self):
        return "{}, {} {}".format(self.last_name.title(), self.first_name.title(),
                                  self.middle_name[:1] + "." if self.middle_name else '')

    @property
    def get_permission(self):
        permission = AuthUserUserPermissions.objects.filter(user_id=self.id).first()
        return permission.permission.name if permission else ''

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Shop(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    search_engine = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    logo = models.FileField(upload_to='shop/logo/')
    status = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    datetime_added = models.DateTimeField(blank=True, null=True, default=timezone.now)
    is_default = models.IntegerField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=150)
    continent = models.CharField(max_length=255)
    se_type = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(AuthUser, related_name='uploaded_by', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'tbl_shop'


class ShopPager(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(Shop, models.DO_NOTHING)
    per_page = models.CharField(max_length=255)
    per_page_value = models.IntegerField(blank=True, null=True)
    total_indicator_class = models.CharField(max_length=255)
    total_indicator_type = models.CharField(max_length=255)
    page_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'tbl_shop_pager'


class ProductClicks(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(Shop, models.DO_NOTHING)
    product_link = models.TextField(blank=True, null=True)
    product_photo = models.TextField(blank=True, null=True)
    product_name = models.TextField(blank=True, null=True)
    product_price = models.DecimalField(max_digits=11, decimal_places=2)
    stock_status = models.TextField(blank=True, null=True)
    date_clicked = models.DateTimeField(blank=True, null=True, default=timezone.now)
    increment = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbl_product_clicks'


class Search(models.Model):
    id = models.BigAutoField(primary_key=True)
    search_data = models.TextField()
    search_input = models.CharField(max_length=100, blank=True, null=True)
    date_search = models.DateField(blank=True, null=True)
    shop = models.ForeignKey(Shop, models.DO_NOTHING)
    is_beta_search = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_search'


class SearchLogs(models.Model):
    id = models.BigAutoField(primary_key=True)
    search_input = models.CharField(max_length=100, blank=True, null=True)
    date_search = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_search_logs'


class ShopScraper(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    wrapper_class = models.CharField(max_length=255)
    link_class = models.CharField(max_length=255)
    image_class = models.CharField(max_length=255)
    price_class = models.CharField(max_length=255)
    stock_status_class = models.CharField(max_length=255)
    content_class = models.CharField(max_length=255, blank=True, null=True)
    product_name_class = models.CharField(max_length=255, blank=True, null=True)
    manufacturer_class = models.CharField(max_length=255, blank=True, null=True)
    wrapper_htype = models.CharField(max_length=255, blank=True, null=True)
    link_htype = models.CharField(max_length=255, blank=True, null=True)
    image_htype = models.CharField(max_length=255, blank=True, null=True)
    price_htype = models.CharField(max_length=255, blank=True, null=True)
    stock_status_htype = models.CharField(max_length=255, blank=True, null=True)
    content_htype = models.CharField(max_length=255, blank=True, null=True)
    product_name_htype = models.CharField(max_length=255, blank=True, null=True)
    manufacturer_htype = models.CharField(max_length=255, blank=True, null=True)
    image_source = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_shop_scraper'


class ShopScraperAdditional(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    link_attribute = models.CharField(max_length=255)
    photo = models.CharField(max_length=255)
    photo_attribute = models.CharField(max_length=255)
    stock_status = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    wrapper = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    is_additional = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tbl_shop_scraper_additional'


class Products(models.Model):
    id = models.AutoField(primary_key=True)
    photo = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=1024, blank=True, null=True)
    price = models.CharField(max_length=10, blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    stock_status = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=255, blank=True, null=True)
    date_search = models.DateField(blank=True, null=True)
    email = models.EmailField()

    class Meta:
        managed = False
        db_table = 'tbl_products'
