import html
import re
import json
import urllib
import urllib3
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from app.backend.models import TblGeneralInfo, TblMembershipPricing, TblSubscription, TblPriceDevelopment, \
    TblSubPriceDevelopment, TblFaq, TblContactUs
from app.models import Shop, ShopScraper, Search, SearchLogs, AuthUser, AuthUserUserPermissions, ProductClicks, \
    ShopPager, ShopScraperAdditional, Products
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import random

from selectolax.parser import HTMLParser


def string_validator(value):
    if value:
        return str(value.text()).strip()
    else:
        return ''


def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


def stock_status_validator(shop_id, status):
    value = status.lower() if status else None
    shop_list = [1, 4]
    if int(shop_id) in shop_list:
        if value:
            if 'out' in value or 'backorder' in value:
                return 'Out of Stock'
            else:
                return 'In Stock'
        else:
            return 'In Stock'
    else:
        if value:
            if 'ausverkauft' in value or 'nicht' in value:
                return 'Out of Stock'
            if 'pre' in value:
                return 'Pre-Order'
            else:
                if value == 'new' or has_numbers(value) or not 'out' in value:
                    return 'In Stock'
                else:
                    return 'Out of Stock'
        else:
            return 'Out of Stock'


def get_symbol(price):
    return re.sub(r'\d+(?:,\d+)*(?:\.\d+)?|\s+', '', price)


def price_correction(value):
    currency_list = []
    for row in Shop.objects.all().order_by('name'):
        currency_list.append(str(row.currency))

    value = value.split('-')[0]
    value = value.replace('*', '').replace('Preis:', '')
    if value:
        if '$' in value:
            if ',' in value:
                value = value.replace(',', '.')
            return re.findall(r'[\d\.\d]+', value)[0]
        else:
            if '€' in value:
                price = value.replace('€', '').replace('\xa0', '').strip()
                return price.replace(".", "").replace(",", ".")
                # return price[:-2].replace(".", "").replace(",", ".")
            else:
                return '0'
    else:
        return '0'


def validate_link(url, link):
    if 'cdn' in link:
        return link
    if link.startswith('/'):
        return url + link
    else:
        return link.replace('/sm/', '/md/').replace('/thumb/', '/')
        # to adjust thumbnail from small to medium; valid values ['/sm/', '/md/', '/lg/', '/xl/']


def login_user(request):
    if request.user.is_authenticated:
        return redirect('landing')
    if request.method == "POST":
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if result['success']:
            if user is not None and user.is_active:
                login(request, user)
                request.session['uid'] = user.id
                request.session['username'] = user.username
                request.session['first_name'] = user.first_name
                messages.success(request, "Welcome", extra_tags="welcome")
                return JsonResponse({'data': 'success'})
            else:
                return JsonResponse({'error': True, 'msg': 'Invalid username and password.'})
        else:
            return JsonResponse({'error': True, 'msg': 'Invalid reCAPTCHA. Please try again.'})
    return render(request, 'login.html')


@login_required
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login_user')


def validate_manufacturer(value):
    return value.replace('Hersteller:', '').replace('Marke:', '').strip()


def landing(request):
    if request.method == "GET":
        if request.GET.get('search_input'):
            SearchLogs.objects.create(
                search_input=request.GET.get('search_input'),
                date_search=date.today()
            )

    most_click_product = ProductClicks.objects.values('product_name').annotate(
        total_clicks=Sum('increment'),
    ).order_by('-total_clicks')[:4]

    context = {
        'title': 'landing',
        'most_click_product': most_click_product,
        'shops': Shop.objects.filter(status=1).order_by('name'),
        'continent': Shop.objects.values('continent').order_by('continent').annotate(count=Count('continent')),
        'countries_count': Shop.objects.values('location').order_by('location').annotate(
            count=Count('location')).filter(
            status=1).count(),
        'countries': Shop.objects.values('location').order_by('location').annotate(count=Count('location')).filter(
            status=1),
        'search_count': SearchLogs.objects.all().count(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first()
    }
    return render(request, 'landing.html', context)


def contact_us(request):
    if request.method == 'POST':
        contact = TblContactUs(
            fullname = request.POST.get('name'),
            email = request.POST.get('email'),
            subject = request.POST.get('subject'),
            message = request.POST.get('message'),
            is_seen = 0,
            is_reply = 0
        )
        contact.save()
        send_mail(
            'RCStock Queries',
            'Thanks for taking the time to give us your queries. We do use everything to query your messages. Thanks - RCStock.net Management',
            'support@rcstock.net',
            [request.POST.get('email')]
        )
        return JsonResponse({'data': 'success', 'msg': 'Your queries successfully send.'})
    users = AuthUser.objects.filter(id = request.user.id).first()
    context = {
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
        'users': users if users else ''
    }
    return render(request, 'contact_us.html', context)


def about(request):
    context = {
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
    }
    return render(request, 'about.html', context)


def data_protection(request):
    context = {
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
    }
    return render(request, 'data_protection.html', context)


def affiliate(request):
    context = {
        'geninfo': TblGeneralInfo.objects.get(id=1),
    }
    return render(request, 'affiliate.html', context)


def faq(request):
    context = {
        'geninfo': TblGeneralInfo.objects.get(id=1),
        'faq': TblFaq.objects.filter(isactive=1)
    }
    return render(request, 'faq.html', context)


@login_required
def user_dashboard(request):
    context = {
        'li': 'dashboard',
        'shops': Shop.objects.filter(status=1).order_by('name'),
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
    }
    return render(request, 'user_dashboard.html', context)


@login_required
def user_market_intelligence_dashboard(request):
    subs = TblSubscription.objects.filter(user_id=request.user.id).first()
    shop = Shop.objects.filter(Q(status=1) & Q(owner_id=request.user.id)).order_by('name')
    rand = lambda: random.randint(0, 255)
    color_others = ('#%02X%02X%02X' % (rand(), rand(), rand()))
    labels_other = []
    data_other = []
    datasets_other = []
    count_click_other = []
    shop_owner = Shop.objects.values_list('id').filter(owner_id=request.user.id)
    other_most_click_product = ProductClicks.objects.values('product_name').filter(~Q(shop__in=shop_owner)
                                                                                   ).annotate(
        count=Count('product_name'),
        )[:5]
    for i in other_most_click_product:
        labels_other.append(i['product_name'])
        count_click_other.append(i['count'])
    datasets_other.append(
        {
            'label': 'Most Clicked Products of other shop',
            'fill': 'false',
            'backgroundColor': color_others,
            'borderColor': color_others,
            'data': count_click_other,
        }
    )
    data_other[:] = []

    r = lambda: random.randint(0, 255)
    color = ('#%02X%02X%02X' % (r(), r(), r()))
    labels = []
    data = []
    datasets = []
    count_click = []
    your_most_click_product = ProductClicks.objects.values('product_name').filter(
        shop__owner_id=request.user.id).annotate(total_clicks=Sum('increment'),
                                           ).order_by('-total_clicks')[:4]
    for i in your_most_click_product:
        labels.append(i['product_name'])
        count_click.append(i['total_clicks'])
    datasets.append(
        {
            'label': 'Most Clicked Products of your shop',
            'fill': 'false',
            'backgroundColor': color,
            'borderColor': color,
            'data': count_click,
        }
    )
    data[:] = []
    context = {
        'datasets': datasets,
        'labels': list(dict.fromkeys(labels)),
        'datasets_other': datasets_other,
        'labels_other': list(dict.fromkeys(labels_other)),
        'li': 'dashboard',
        'shops': shop if shop else '',
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
        'subscription': subs if subs else '',
        'membership_pricing': TblMembershipPricing.objects.filter(is_active=1).order_by('price'),
        'your_most_click_product': your_most_click_product,
        'other_most_click_product': other_most_click_product,
        'stock_in': ProductClicks.objects.filter(stock_status='In Stock').order_by('-date_clicked'),
        'stock_out': ProductClicks.objects.filter(stock_status='Out of Stock').order_by('-date_clicked')
    }
    return render(request, 'user_market_intelligence_dashboard.html', context)


@login_required
def user_market_intelligence_shops(request, pk, owner_id):
    today = date.today()
    search_cache = Search.objects.filter(Q(shop_id=pk) & Q(date_search=today) & Q(shop__owner_id=owner_id)).order_by(
        '-date_search').first()
    datas = sorted(eval(search_cache.search_data), key=lambda e: (float(e['price'])))

    prices = []
    if datas:
        for row in datas:
            prices.append(float(row['price']))

    context = {
        'datas': datas,
        'shops': Shop.objects.filter(status=1).order_by('name'),
        'shop': Shop.objects.filter(id=pk).first()
    }
    return render(request, 'user_market_intelligence_shops.html', context)


@login_required
def user_account(request):
    if request.method == "POST":
        AuthUser.objects.filter(id=request.user.id).update(
            username=request.POST.get('username'),
            first_name=request.POST.get('fname'),
            last_name=request.POST.get('lname'),
            middle_name=request.POST.get('mname') if request.POST.get('mname') else None,
            email=request.POST.get('email'),
            address=request.POST.get('address')
        )
        return JsonResponse({'data': 'success', 'msg': 'Your information has been changed successfully updated.'})
    subs = TblSubscription.objects.filter(user_id=request.user.id).first()
    context = {
        'li': 'user_account',
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
        'users': AuthUser.objects.filter(id=request.user.id).first(),
        'subscription': subs if subs else '',
        'membership_pricing': TblMembershipPricing.objects.filter(is_active=1).order_by('price')
    }
    return render(request, 'user_account.html', context)


@login_required
def user_changepassword(request):
    if request.method == "POST":
        check = User.objects.get(id=request.user.id)
        if request.POST.get('new_password1') == request.POST.get('new_password2'):
            if check.check_password(request.POST.get('current_password')):
                AuthUser.objects.filter(id=request.user.id).update(
                    password=make_password(request.POST.get('new_password1'))
                )
                return JsonResponse({'data': 'success', 'title': 'Password Changed!', 'msg': 'Your password has been '
                                                                                             'changed successfully.'})
            else:
                return JsonResponse({'error': True, 'msg': 'The current password you entered is invalid. Please try '
                                                           'again'})
        else:
            return JsonResponse({'error': True, 'msg': 'Your confirmation password does not match the new password'})
    context = {
        'li': 'user_changepassword',
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
    }
    return render(request, 'user_changepassword.html', context)


@csrf_exempt
def market_intelligence(request, status=None):
    if request.method == "POST":
        check_email = AuthUser.objects.filter(email = request.POST.get('email'))
        check_username = AuthUser.objects.filter(username=request.POST.get('uname'))
        if check_email:
            return JsonResponse({'error': True, 'msg': 'Email already exist.'})
        elif check_username:
            return JsonResponse({'error': True, 'msg': 'Username already exist.'})
        else:
            users = AuthUser(
                first_name=strip_tags(request.POST.get('fname')),
                last_name=strip_tags(request.POST.get('lname')),
                middle_name=strip_tags(request.POST.get('mname')),
                email=strip_tags(request.POST.get('email')),
                username=strip_tags(request.POST.get('uname')),
                password=make_password(request.POST.get('password1')),
                is_superuser=0,
                is_staff=0,
                is_active=1,
                date_joined=datetime.now(),
                address=strip_tags(request.POST.get('address')),
            )
            users.save()
            user_permission = AuthUserUserPermissions.objects.create(
                user_id=users.id,
                permission_id=103
            )
            return JsonResponse({'user_id': users.id})

    if 'paypal_payment_status' in request.session and 'paypal_payment_message' in request.session:
        title = request.session['paypal_payment_title']
        message = request.session['paypal_payment_message']
        status = request.session['paypal_payment_status']
        del request.session['paypal_payment_message']
        del request.session['paypal_payment_status']
    else:
        title = None
        message = None
        status = None
    context = {
        'geninfo': TblGeneralInfo.objects.filter(id=1).first(),
        'gen_info': TblGeneralInfo.objects.filter(id=1).first(),
        'membership_pricing': TblMembershipPricing.objects.filter(is_active=1).order_by('price'),
        'title': title,
        'status': status,
        'message': message
    }
    return render(request, 'market_intelligence.html', context)
def generate_invoice():
    return str('{}-{}'.format('%4x' % random.getrandbits(2 * 8), '%8x' % random.getrandbits(4 * 8))).upper()

def subscribe_free(request):
    if request.method == "POST":
        check_email = AuthUser.objects.filter(email=request.POST.get('f_email'))
        check_username = AuthUser.objects.filter(username=request.POST.get('f_uname'))
        if check_email:
            return JsonResponse({'error': True, 'msg': 'Email already exist.'})
        elif check_username:
            return JsonResponse({'error': True, 'msg': 'Username already exist.'})
        else:
            invoice = generate_invoice()
            while TblSubscription.objects.filter(invoice=invoice).first() is not None:
                invoice = generate_invoice()

            users = AuthUser(
                first_name=strip_tags(request.POST.get('f_fname')),
                last_name=strip_tags(request.POST.get('f_lname')),
                middle_name=strip_tags(request.POST.get('f_mname')),
                email=strip_tags(request.POST.get('f_email')),
                username=strip_tags(request.POST.get('f_uname')),
                password=make_password(request.POST.get('f_password1')),
                is_superuser=0,
                is_staff=0,
                is_active=1,
                date_joined=datetime.now(),
                address=strip_tags(request.POST.get('f_address')),
            )
            users.save()
            AuthUserUserPermissions.objects.create(
                user_id=users.id,
                permission_id=103
            )
            TblSubscription.objects.create(
                user_id=users.id,
                membership_id=2,
                created_at=datetime.now(),
                status=1,
                invoice=invoice
            )
            return JsonResponse({'data': 'success', 'msg': 'You have successfully subscribed to RCStock. Thank you!'})

@csrf_exempt
def product_click(request, pk):
    if request.method == "POST":
        curr_month = date.today().strftime("%Y-%m")
        exists = ProductClicks.objects.filter(product_name=request.POST.get('product_name'),
                                              shop_id=pk, date_clicked__startswith=curr_month).first()
        if exists:
            exists.date_clicked = datetime.now()
            exists.increment = exists.increment + 1
            exists.save()
        else:
            ProductClicks.objects.create(
                shop_id=pk,
                product_link=request.POST.get('product_link'),
                product_name=request.POST.get('product_name'),
                product_photo=request.POST.get('product_img'),
                product_price=request.POST.get('product_price'),
                stock_status=request.POST.get('product_status'),
                increment=1
            )

        return JsonResponse({'data': 'success'})


# using beautifulsoup
def search_results(request, search_input, pk, beta_search):
    today = date.today()
    search_cache = Search.objects.filter(search_input=search_input.lower(), date_search=today, shop_id=pk,
                                         is_beta_search=beta_search).order_by('-id').first()
    datas = sorted(eval(search_cache.search_data), key=lambda e: (float(e['price'])))

    prices = []
    if datas:
        for row in datas:
            prices.append(float(row['price']))

    context = {
        'datas': datas,
        'total_results': len(datas),
        'search_input': search_input,
        'beta_search': beta_search,
        'pk': pk,
        'min_price': min(prices) if datas else None,
        'max_price': max(prices) if datas else None,
        'shops': Shop.objects.filter(status=1).order_by('name'),
        'shop': Shop.objects.filter(id=pk).first()
    }
    return render(request, 'search_results.html', context)


@csrf_exempt
def price_development(request, prod_name):
    print('hello')
    if request.method == "POST":
        check = TblPriceDevelopment.objects.filter(product_name=request.POST.get('product_name')).all()
        if not check:
            price_dev = TblPriceDevelopment.objects.create(
                product_name=request.POST.get('product_name'),
            )
            TblSubPriceDevelopment.objects.create(
                prod_id=price_dev.id,
                price=request.POST.get('product_price')
            )
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'data': 'warning', 'msg': 'Already Exist!'})
    labels = []
    data = []
    datasets = []
    prod = TblPriceDevelopment.objects.filter(product_name=prod_name).first()
    product_info = TblSubPriceDevelopment.objects.values('price', 'created_at').annotate(
        dcount=Count('price')).filter(prod_id=prod.id).all()
    for i in product_info:
        labels.append(i['created_at'].strftime("%m/%d/%Y"))
        data.append(float(i['price']))
    r = lambda: random.randint(0, 255)
    color = ('#%02X%02X%02X' % (r(), r(), r()))
    datasets.append(
        {
            'data': data.copy(),
            'label': prod.product_name,
            'fill': 'false',
            'backgroundColor': color,
            'borderColor': color,
        }
    )
    data[:] = []
    print('datasets', datasets)
    context = {
        'products': prod,
        'prod_name': prod_name,
        'product_info': product_info,
        'datasets': datasets,
        'labels': list(dict.fromkeys(labels)),
    }
    return render(request, 'price_development.html', context)


# using selectolax and urllib3
def search_results_v2(request, search_input, pk, beta_search):
    today = date.today()
    datas = []
    search_cache = Search.objects.filter(search_input=search_input.lower().strip(), date_search=today, shop_id=pk,
                                         is_beta_search=beta_search).order_by('-id').first()
    clicks = ProductClicks.objects.filter(shop_id=pk).annotate(inc=Sum('increment')) \
                 .values_list('product_name', 'shop__name', 'inc').all()[:10]

    # SORTING BY CLICKS
    if search_cache:
        if search_cache.search_data:
            datas = eval(search_cache.search_data)
            for x in datas:
                x['increment'] = 0
                for c in clicks:
                    if c[0] == x['product_name'] and c[1] == x['shop']:
                        x['increment'] = c[2]
            datas = sorted(datas, key=lambda e: (float(e['increment'])), reverse=True)

    # REMOVED SORTING BY PRICE
    # if search_cache:
    #     if search_cache.search_data:
    #         datas = sorted(eval(search_cache.search_data), key=lambda e: (float(e['price'])))

    prices = []
    for row in datas:
        prices.append(float(row['price']))

    context = {
        'datas': datas,
        'total_results': len(datas),
        'search_input': search_input,
        'beta_search': beta_search,
        'pk': pk,
        'min_price': min(prices) if datas else None,
        'max_price': max(prices) if datas else None,
        'shops': Shop.objects.filter(status=1).order_by('name'),
        'shop': Shop.objects.filter(id=pk).first(),
        'additional': ShopScraperAdditional.objects.filter(shop_id=pk).first(),
        'per_page': 15
    }
    return render(request, 'search_results_v2.html', context)


# using selectolax and urllib3
def make_soup_v2(soup, row, pk, search_input, additional=None, url=None):
    http = urllib3.PoolManager()
    data = []
    sku = ''
    s = soup.css_first('{}.{}'.format(str(row.wrapper_htype), str(row.wrapper_class)))  # Wrapper Class
    if not s:
        s = soup.css_first('{}#{}'.format(str(row.wrapper_htype), str(row.wrapper_class)))  # Wrapper ID

    try:
        lines = s.css('{}.{}'.format(str(row.content_htype), str(row.content_class))) \
            if row.content_htype and row.content_class else s.css(str(row.content_htype))
    except Exception as e:
        lines = None

    if lines:
        for line in lines:
            try:
                photo = str(line.css_first('{}.{}'.format(str(row.image_htype), str(row.image_class))).attrs[
                                str(row.image_source)]).strip() \
                    if row.image_htype and row.image_class \
                    else str(line.css_first(str(row.image_htype)).attrs[str(row.image_source)]).strip()
            except Exception as e:
                photo = ""

            link = line.css_first('{}.{}'.format(str(row.link_htype), str(row.link_class))).attrs['href'] \
                if row.link_htype and row.link_class else line.css_first(str(row.link_htype)).attrs['href']

            product_name = line.css_first('{}.{}'.format(str(row.product_name_htype), str(row.product_name_class))) \
                if row.product_name_htype and row.product_name_class else line.css_first(str(row.product_name_htype))

            manufacturer = string_validator(product_name).split()[0] \
                if str(row.manufacturer_class) == 'first_word' \
                else string_validator(line.css_first('{}.{}'.format(row.manufacturer_htype,
                                                                    row.manufacturer_class)))

            price = line.css_first('{}.{}'.format(str(row.price_htype), str(row.price_class))) \
                if row.price_htype and row.price_class \
                else line.css_first(str(row.price_htype))

            if additional:
                url_addtl = validate_link(row.shop.url, link)
                r_addtl = http.request('GET', html.unescape(url_addtl))
                soup_addtl = HTMLParser(r_addtl.data.decode('utf-8'))

                info = get_soup_details(soup_addtl, additional, pk)
                sku = info['sku']
                stock_status = info['stock_status']
            else:
                stock_status = line.css_first('{}.{}'.format(str(row.stock_status_htype),
                                                             str(row.stock_status_class))) \
                    if row.stock_status_htype and row.stock_status_class \
                    else line.css_first(str(row.stock_status_htype))

                stock_status = stock_status_validator(pk, string_validator(stock_status)) if stock_status \
                    else stock_status_validator(pk, None)

            if row.shop.se_type == 1:
                if search_input.lower() in string_validator(product_name).lower():
                    data.append({
                        'photo': validate_link(row.shop.url, photo.replace("60x", "400x").split(',')[0]),
                        'manufacturer': validate_manufacturer(manufacturer),
                        'product_name': string_validator(product_name),
                        'price': price_correction(string_validator(price)) if price else '0',
                        'link': validate_link(row.shop.url, link),
                        'shop': row.shop.name,
                        'sku': sku,
                        'stock_status': stock_status
                    })
            else:
                data.append({
                    'photo': validate_link(row.shop.url, photo.replace("60x", "400x").split(',')[0]),
                    'manufacturer': validate_manufacturer(manufacturer),
                    'product_name': string_validator(product_name),
                    'price': price_correction(string_validator(price)) if price else '0',
                    'link': validate_link(row.shop.url, link),
                    'shop': row.shop.name,
                    'sku': sku,
                    'stock_status': stock_status
                })
    else:
        if additional:
            aa = make_soup_v2_additional(soup, additional, pk, search_input.lower(), url)
            data.extend(aa)
    return data


def get_soup_details(soup, row, pk):
    data = {'stock_status': '', 'sku': ''}
    try:
        lines = soup.css(str(row.wrapper))
    except Exception as e:
        lines = None

    if lines:
        for line in lines:
            stock_status = line.css_first(str(row.stock_status))
            if stock_status:
                data['stock_status'] = stock_status_validator(pk, string_validator(stock_status)) if stock_status \
                    else stock_status_validator(pk, None)
                data['sku'] = line.css_first(str(row.sku)).text().replace("SKU", "").strip() if row.sku else ''
    return data


def make_soup_v2_additional(soup, row, pk, search_input, url):
    data = []

    try:
        lines = soup.css(str(row.wrapper))
    except Exception as e:
        lines = None

    if lines:
        for line in lines:
            try:
                photo = str(line.css_first(str(row.photo)).attrs[
                                str(row.photo_attribute)]).strip()
            except Exception as e:
                photo = ""

            product_name = line.css_first(str(row.product_name))

            manufacturer = string_validator(line.css_first('{}'.format(row.manufacturer))) if row.manufacturer else ''

            price = line.css_first(str(row.price))

            sku = line.css_first(str(row.sku)).text().replace("SKU", "").strip() if row.sku else ''

            stock_status = line.css_first(str(row.stock_status))
            stock_status = stock_status_validator(pk, string_validator(stock_status)) if stock_status \
                else stock_status_validator(pk, None)

            if row.shop.se_type == 1:
                if search_input.lower() in string_validator(product_name).lower():
                    data.append({
                        'photo': validate_link(row.shop.url, photo.replace("60x", "400x").split(',')[0]),
                        'manufacturer': validate_manufacturer(manufacturer),
                        'product_name': string_validator(product_name),
                        'price': price_correction(string_validator(price)) if price else '0',
                        'link': url,
                        'shop': row.shop.name,
                        'sku': sku,
                        'stock_status': stock_status
                    })
            else:
                data.append({
                    'photo': validate_link(row.shop.url, photo.replace("60x", "400x").split(',')[0]),
                    'manufacturer': validate_manufacturer(manufacturer),
                    'product_name': string_validator(product_name),
                    'price': price_correction(string_validator(price)) if price else '0',
                    'link': url,
                    'shop': row.shop.name,
                    'sku': sku,
                    'stock_status': stock_status
                })
    else:
        data = []
    return data


# using selectolax and urllib3
def process_search_results_v2(request, search_input, pk, beta_search):
    http = urllib3.PoolManager()
    if request.method == "GET":
        shop = ShopScraper.objects.filter(shop_id=pk)
        search = search_input.replace(' ', '%20')
        today = date.today()

        # check = False
        check = Search.objects.filter(search_input=search_input.lower(),
                                      date_search=today, shop_id=pk, is_beta_search=beta_search)
        if not check:
            for row in shop:
                data = []

                pager = ShopPager.objects.filter(shop_id=pk).first()
                pagination = '{}{}'.format(pager.per_page, pager.per_page_value) if pager else ''
                per_page_value = pager.per_page_value if pager else 0

                url = str(row.shop.search_engine) + search + pagination
                r = http.request('GET', html.unescape(url))
                soup = HTMLParser(r.data.decode('utf-8'))

                additional = ShopScraperAdditional.objects.filter(Q(shop_id=pk), Q(is_additional=1)).first()
                data.extend(make_soup_v2(soup, row, pk, search_input.lower(), additional, url))

                # save daan ang results sa first page
                # para dili tibo ang results
                # incase dugay, naa nay mag-una daan nga results
                src_obj = Search.objects.create(
                    search_data=data,
                    search_input=search_input.lower().strip(),
                    date_search=today,
                    shop_id=pk,
                    is_beta_search=beta_search
                )

                # check if naa pay lain page
                # mucheck lang ka kung ang data kay niabot ug 1 or more
                if pager and data and len(data) > 0:
                    total_indicator_type = pager.total_indicator_type
                    total_indicator_class = pager.total_indicator_class
                    searched = soup.css_first('{}.{}'.format(str(total_indicator_type), str(total_indicator_class)))

                    # processing for shop-independent cases
                    searched = string_validator(searched)
                    if row.shop.id == 5 or row.shop.id == 6:
                        searched = searched[searched.find('(') + 1:searched.find(')')] if '(' in searched else 0
                    elif row.shop.id == 10:
                        searched = ''.join(i for i in searched if i.isdigit())
                    elif row.shop.id == 3:
                        searched = searched.replace(u'\xa0', u' ').replace(u'\n', u' ').replace('         ', ' ')
                        searched = searched[searched.find('von') + 3:searched.find('Ergebnisse')].strip()
                    elif row.shop.id == 13:
                        searched = searched.replace(u'\xa0', u' ').replace(u'\n', u' ').replace('         ', ' ')
                        searched = searched[searched.find('of') + 2:searched.find('Result')].strip()
                    else:
                        searched = searched.replace('results', '').replace('result', '')

                    total_searched = int(searched)
                    total_pages = (total_searched // per_page_value) + (
                        0 if ((total_searched % per_page_value) == 0) else 1)

                    if total_pages >= 2:
                        for y in range(2, total_pages + 1):
                            url = '{}{}{}'.format(str(row.shop.search_engine) + search + pagination,
                                                  pager.page_url, y)
                            r = http.request('GET', html.unescape(url))
                            soup = HTMLParser(r.data.decode('utf-8'))
                            data.extend(make_soup_v2(soup, row, pk, search_input, additional, url))

                            # update nalang dayon sa results kada page
                            # so that, naay movement sab sa number of na-scrape
                            src_obj.search_data = data
                            src_obj.save()

        search_cache = Search.objects.filter(search_input=search_input.lower(), date_search=today, shop_id=pk,
                                             is_beta_search=beta_search).first()
        return JsonResponse({'total_results': len(eval(search_cache.search_data)), 'pk': pk})


def get_in_stock(request, search_input, pk, beta_search):
    today = date.today()
    search_cache = Search.objects.filter(search_input=search_input.lower(), date_search=today, shop_id=pk,
                                         is_beta_search=beta_search).first()
    results = []
    for row in eval(search_cache.search_data):
        if row['stock_status'] == 'In Stock' or row['stock_status'] == 'Pre-Order':
            results.append({'photo': row['photo'],
                            'manufacturer': row['manufacturer'],
                            'product_name': row['product_name'],
                            'price': row['price'],
                            'link': row['link'],
                            'shop': row['shop'],
                            'stock_status': row['stock_status']
                            })

    return JsonResponse({'total_results': len(results), 'pk': pk})


def get_all_stock(request, search_input, pk, beta_search):
    today = date.today()
    search_cache = Search.objects.filter(search_input=search_input.lower(), date_search=today, shop_id=pk,
                                         is_beta_search=beta_search).first()
    return JsonResponse({'total_results': len(eval(search_cache.search_data)), 'pk': pk})


def autocomplete_suggestions(request):
    if request.method == "GET":
        json = []
        search = Search.objects.values('search_input').order_by('search_input').annotate(
            count=Count('search_input')
        ).filter(Q(search_input__icontains=request.GET.get('query')))[:10]

        for row in search:
            json.append(row['search_input'])

        return JsonResponse(json, safe=False)


@csrf_exempt
def notify_me(request):
    today = date.today()
    if request.method == 'POST':
        check = Products.objects.filter(product_name=request.POST.get('product_name'),
                                        email=request.POST.get('email')).all()
        if not check:
            Products.objects.create(
                photo=request.POST.get('photo'),
                manufacturer=request.POST.get('manufacturer'),
                product_name=request.POST.get('product_name'),
                price=request.POST.get('price'),
                link=request.POST.get('link'),
                shop_id=request.POST.get('shop_id'),
                stock_status=request.POST.get('stock_status'),
                date_search=today,
                email=request.POST.get('email'),
                sku=request.POST.get('sku')
            )

            message = 'Thank you for your interest in this item: <strong>{}</strong>. We are going to notify you via ' \
                      'this email: <strong>{}</strong>, ' \
                      'whenever this item becomes available. - The RCStock Management'.format(
                request.POST.get('product_name'), request.POST.get('email'))
            send_mail(
                'RCStock Notification Subscription',
                strip_tags(message),
                'support@rcstock.net',
                [request.POST.get('email')],
                html_message=message
            )

            return JsonResponse(
                {'data': 'success', 'msg': message.replace(' - The RCStock Management', ''), 'title': 'Success'})
        else:
            return JsonResponse({'data': 'warning', 'msg': 'You have already subscribed to notifications '
                                                           'for the item: <strong>{}</strong>.'.format(
                request.POST.get('product_name')), 'title': 'Already Subscribed'})
    else:
        return JsonResponse({'data': 'error', 'msg': 'You are not allowed to continue this transaction.',
                             'title': 'Unauthorized'})
