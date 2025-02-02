import hashlib
import json

from django import template
from django.core.serializers import serialize

from app.backend.models import TblGeneralInfo, TblSubscription
from app.models import ProductClicks, Search, AuthUserUserPermissions
from datetime import timedelta, date, datetime, timezone
from django.db.models import Q, QuerySet

register = template.Library()


@register.simple_tag
def getHash(string):
    return hashlib.sha1(str(string).encode('utf-8')).hexdigest()


@register.simple_tag
def get_rcstock_logo():
    gen_info = TblGeneralInfo.objects.filter(id=1).first()
    return gen_info.picture


@register.simple_tag
def get_most_click_product_info(product_name):
    return ProductClicks.objects.filter(product_name=product_name).first()


@register.simple_tag
def get_most_click_product_owner_shop(product_name, owner_id):
    prod_clicks = ProductClicks.objects.filter(shop__owner_id=owner_id).first()
    return prod_clicks


# @register.simple_tag
# def get_other_noturs_most_click_product(owner_id):
#     prod_clicks = ProductClicks.objects.filter(Q(shop__in=shop)).first()
#     print(prod_clicks)
#     return prod_clicks


@register.simple_tag
def get_subscribe(id, user_id):
    subs = TblSubscription.objects.filter(membership_id=id, user_id=user_id, status=1).first()
    return subs


@register.simple_tag
def get_valid_until(id, user_id):
    valid_until = TblSubscription.objects.filter(membership_id=id, user_id=user_id).first()
    if valid_until:
        start_date = datetime.now(timezone.utc)
        date_created = valid_until.created_at
        date_months = date_created + timedelta(days=30)
        total = date_months - start_date
        total = total.days
        if total <= 0:
            return date_months.strftime('%B %d, %Y')
        else:
            return date_months.strftime('%B %d, %Y')


@register.simple_tag
def get_date_duration_days(id, user_id):
    valid_until = TblSubscription.objects.filter(membership_id=id, user_id=user_id).first()
    if valid_until:
        start_date = datetime.now(timezone.utc)
        date_created = valid_until.created_at
        date_months = date_created + timedelta(days=30)
        total = date_months - start_date
        total = total.days
        if 2 <= total:
            return '{} days remaining'.format(total)
        elif total <= 0 or total <= 1:
            return '{} day remaining'.format(total)


@register.simple_tag
def check_permission(user_id):
    permission = AuthUserUserPermissions.objects.filter(Q(user_id=user_id) & Q(permission=103)).first()
    return permission


@register.simple_tag
def convert_days_to_month(dt):
    if dt:
        td = (dt%365)//30
        if td > 1:
            return "{} months".format(td)
        else:
            return "{} month".format(td)


@register.simple_tag
def get_products_available_on_the_shop(search_input, beta_search):
    today = date.today()
    search_cache = Search.objects.filter(search_input=search_input.lower(), date_search=today,
                                         is_beta_search=beta_search)
    total_results = 0
    shop = []
    for row in search_cache:
        if row.search_data:
            for i in eval(row.search_data):
                total_results += 1

                if not i['shop'] in shop:
                    shop.append(i['shop'])

    return [total_results, len(shop)]


@register.simple_tag
def check_if_multiple_of(m, n):
    return [n for n in range(1, n+1) if n % m == 0]


@register.simple_tag
def get_index(haystack, needle):
    return haystack.index(needle)


@register.simple_tag
def get_pages(haystack, m):
    return (len(haystack) // m) + (1 if len(haystack) % m != 0 else 0)


@register.filter(is_safe=True)
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return serialize('json', obj)
    return json.dumps(obj)
