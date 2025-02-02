import json
import urllib
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from app.backend.forms import UploadLogoForm, UploadShopLogoForm
from app.backend.models import Loghistory, TblGeneralInfo, TblMembershipPricing, TblSubscription, TblFaq, \
    TblContactUs, TblContactUsReply
from app.models import AuthUser, Shop, ShopScraper, AuthPermission, AuthUserUserPermissions, SearchLogs, \
    ShopScraperAdditional

from rcstockv2 import settings
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


def log_history(user, descriptions):
    logs = Loghistory(
        user_id=user,
        descriptions=descriptions
    )
    logs.save()


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
                log_history(request.user.id, 'Logged in user: {}'.format(request.session['first_name']))
                messages.success(request, "Welcome", extra_tags="welcome")
                return JsonResponse({'data': 'success'})
            else:
                return JsonResponse({'error': True, 'msg': 'Invalid username and password.'})
        else:
            return JsonResponse({'error': True, 'msg': 'Invalid reCAPTCHA. Please try again.'})
    return render(request, 'backend/login.html')


@login_required
def sign_out(request):
    if request.user.is_authenticated:
        log_history(request.user.id,
                    '{} has signed out.'.format(request.session['first_name']))
        logout(request)
        return redirect('sign_in')


def registration(request):
    return render(request, 'backend/sign_up.html')


@login_required(login_url='sign_in')
def dashboard(request):
    context = {
        'user': AuthUser.objects.all().count(),
        'active_shops': Shop.objects.filter(status=1).count(),
        'prod_search': SearchLogs.objects.all().count(),
        'li': 'dashboard',
        'tabs_name': 'Dashboard'
    }
    return render(request, 'backend/dashboard.html', context)


@login_required(login_url='sign_in')
def list_of_shop(request):
    if request.method == "POST":
        check = Shop.objects.filter(name=request.POST.get('shop_name'))
        if check:
            return JsonResponse({'data': 'error', 'msg': 'Shop duplicate entry.'})
        else:
            attachment = request.FILES.get('shop_logo')
            iOneMore = Shop.objects.last().id + 1
            shop = Shop(
                id=iOneMore,
                name=request.POST.get('shop_name'),
                logo=attachment,
                location=request.POST.get('location'),
                language=request.POST.get('language'),
                status=1 if request.POST.get('status') else 0,
                is_default=1 if request.POST.get('is_default') else 0,
                uploaded_by_id=request.user.id,
                search_engine=request.POST.get('search_engine'),
                se_type=request.POST.get('se_type'),
                url=request.POST.get('url'),
                currency=request.POST.get('currency'),
                continent=request.POST.get('continent')
            )
            shop.save()
            log_history(request.user.id, '{} added new shop {}.'.format(request.session['first_name'],
                                                                        request.POST.get('shop_name')))
            return JsonResponse({'data': 'success', 'msg': 'You have successfully added new shop.'})
    context = {
        'li': 'shops',
        'tabs_name': 'Shops',
        'shop': Shop.objects.all().order_by('-datetime_added')
    }
    return render(request, 'backend/listof_shop.html', context)


@login_required
def update_shop(request, pk):
    if request.method == "POST":
        update_shop = Shop.objects.filter(id=request.POST.get('update-id')).first()
        update_shop.name = request.POST.get('edit_shop_name')
        update_shop.location = request.POST.get('edit_location')
        update_shop.language = request.POST.get('edit_language')
        update_shop.status = 1 if request.POST.get('edit_status') else 0
        update_shop.is_default = 1 if request.POST.get('edit_is_default') else 0
        update_shop.search_engine = request.POST.get('edit_search_engine')
        update_shop.url = request.POST.get('edit_url')
        update_shop.currency = request.POST.get('edit_currency')
        update_shop.continent = request.POST.get('edit_continent')
        update_shop.se_type = request.POST.get('edit_se_type')
        update_shop.save()
        log_history(request.user.id, '{} updating the shop {}.'.format(request.session['first_name'],
                                                                       request.POST.get('edit_shop_name')))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the shop.'})
    upload_shop_logo = UploadShopLogoForm(instance=get_object_or_404(Shop, pk=pk))
    context = {
        'shop': Shop.objects.get(id=pk),
        'pk': pk,
        'uploadshoplogo_form': upload_shop_logo,
    }
    return render(request, 'backend/update_shop.html', context)


@login_required
def upload_shoplogo(request, pk):
    obj = get_object_or_404(Shop, pk=pk)
    form = UploadShopLogoForm(request.POST, request.FILES, instance=obj)
    if request.method == "POST":
        if form.is_valid():
            logo = form.save(commit=False)
            logo.save()
            form.save()
    return JsonResponse({'data': 'success', 'msg': 'Shop logo photo was updated.', 'logo': obj.logo.url})


@login_required(login_url='sign_in')
def list_of_shop_scrapper(request):
    if request.method == "POST":
        s = Shop.objects.filter(id=request.POST.get('shop_name')).first()
        iOneMore = ShopScraper.objects.last().id + 1
        check = ShopScraper.objects.filter(shop_id=request.POST.get('shop_name'))
        if check:
            return JsonResponse({'data': 'error', 'msg': 'Shop scraper duplicate entry.'})
        else:
            scrapper = ShopScraper(
                id=iOneMore,
                shop_id=request.POST.get('shop_name') if request.POST.get('shop_name') else None,
                image_source=request.POST.get('img_source') if request.POST.get('img_source') else None,
                product_name_class=request.POST.get('product_name_class') if request.POST.get(
                    'product_name_class') else None,
                wrapper_class=request.POST.get('wrapper_class') if request.POST.get('wrapper_class') else None,
                link_class=request.POST.get('link_class') if request.POST.get('link_class') else None,
                image_class=request.POST.get('img_class') if request.POST.get('img_class') else None,
                price_class=request.POST.get('price_class') if request.POST.get('price_class') else None,
                stock_status_class=request.POST.get('stock_status_class') if request.POST.get(
                    'stock_status_class') else None,
                content_class=request.POST.get('content_class') if request.POST.get('content_class') else None,
                manufacturer_class=request.POST.get('manufacturer_class') if request.POST.get(
                    'manufacturer_class') else None,
                wrapper_htype=request.POST.get('wrapper_htype') if request.POST.get('wrapper_htype') else None,
                link_htype=request.POST.get('link_htype') if request.POST.get('link_htype') else None,
                image_htype=request.POST.get('img_htype') if request.POST.get('img_htype') else None,
                price_htype=request.POST.get('price_htype') if request.POST.get('price_htype') else None,
                stock_status_htype=request.POST.get('stck_status_htype') if request.POST.get(
                    'stck_status_htype') else None,
                content_htype=request.POST.get('content_htype') if request.POST.get('content_htype') else None,
                product_name_htype=request.POST.get('product_name_htype') if request.POST.get(
                    'product_name_htype') else None,
                manufacturer_htype=request.POST.get('manufacturer_htype') if request.POST.get(
                    'manufacturer_htype') else None,
            )
            scrapper.save()
            log_history(request.user.id, '{} added new shop scrapper {}.'.format(request.session['first_name'],
                                                                                 s.name))
            return JsonResponse({'data': 'success', 'msg': 'You have successfully added new shop scrapper.'})
    context = {
        'li': 'shop_scrapper',
        'tabs_name': 'Shop Scraper',
        'shop': Shop.objects.filter(status=1)
    }
    return render(request, 'backend/listof_shop_scrapper.html', context)


@login_required
def update_shop_scrapper(request, pk):
    if request.method == "POST":
        ShopScraper.objects.filter(shop_id=pk).update(
            wrapper_class=request.POST.get('edit_wrapper_class'),
            wrapper_htype=request.POST.get('edit_wrapper_htype'),
            content_class=request.POST.get('edit_content_class'),
            content_htype=request.POST.get('edit_content_htype'),
            image_class=request.POST.get('edit_img_class'),
            image_htype=request.POST.get('edit_img_htype'),
            image_source=request.POST.get('edit_img_source'),
            product_name_class=request.POST.get('edit_product_name_class'),
            product_name_htype=request.POST.get('edit_product_name_htype'),
            link_class=request.POST.get('edit_link_class'),
            link_htype=request.POST.get('edit_link_htype'),
            price_class=request.POST.get('edit_price_class'),
            price_htype=request.POST.get('edit_price_htype'),
            manufacturer_class=request.POST.get('edit_manufacturer_class'),
            manufacturer_htype=request.POST.get('edit_manufacturer_htype'),
            stock_status_htype=request.POST.get('edit_stock_status_htype'),
            stock_status_class=request.POST.get('edit_stock_status_class'),
        )

        check_additional = ShopScraperAdditional.objects.filter(shop_id=pk)
        if not check_additional:
            increment = ShopScraperAdditional.objects.all().last()
            ShopScraperAdditional.objects.create(
                id=increment.id + 1 if increment else 1,
                wrapper=request.POST.get('wrapper_additional'),
                product_name=request.POST.get('product_name_additional'),
                manufacturer=request.POST.get('manufacturer_additional'),
                link=request.POST.get('link_additional'),
                link_attribute=request.POST.get('link_attribute_additional'),
                photo=request.POST.get('photo_additional'),
                photo_attribute=request.POST.get('photo_attribute_additional'),
                stock_status=request.POST.get('stock_status_additional'),
                price=request.POST.get('price_additional'),
                sku=request.POST.get('sku_additional'),
                shop_id=pk,
            )
        else:
            check_additional.update(
                wrapper=request.POST.get('wrapper_additional'),
                product_name=request.POST.get('product_name_additional'),
                manufacturer=request.POST.get('manufacturer_additional'),
                link=request.POST.get('link_additional'),
                link_attribute=request.POST.get('link_attribute_additional'),
                photo=request.POST.get('photo_additional'),
                photo_attribute=request.POST.get('photo_attribute_additional'),
                stock_status=request.POST.get('stock_status_additional'),
                price=request.POST.get('price_additional'),
                sku=request.POST.get('sku_additional'),
            )

        data = ShopScraper.objects.filter(id=pk).first()
        log_history(request.user.id, '{} updating the shop scrapper {}.'.format(request.session['first_name'],
                                                                                data.shop.name))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the shop.'})
    context = {
        'pk': pk,
        'scrapper': ShopScraper.objects.filter(shop_id=pk).first(),
        'additional_scrapper': ShopScraperAdditional.objects.filter(shop_id=pk).first(),
        'shop': Shop.objects.filter(status=1)
    }
    return render(request, 'backend/update_shop_scrapper.html', context)


@login_required(login_url='sign_in')
def list_of_suppliers(request):
    context = {
        'li': 'suppliers',
        'li_tab': 'users',
        'tabs_name': 'Supplier',
    }
    return render(request, 'backend/list_of_supplier.html', context)


@login_required(login_url='sign_in')
def list_of_users(request):
    if request.method == "POST":
        checked = AuthUser.objects.filter(
            Q(first_name=request.POST.get('fname')) & Q(last_name=request.POST.get('lname')))
        if checked:
            return JsonResponse({'data': 'error', 'msg': 'Duplicate entry of user.'})
        else:
            user = AuthUser(
                first_name=strip_tags(request.POST.get('fname')),
                last_name=strip_tags(request.POST.get('lname')),
                middle_name=strip_tags(request.POST.get('mname')),
                email=strip_tags(request.POST.get('email')),
                username=strip_tags(request.POST.get('uname')),
                password=make_password(request.POST.get('password1')),
                is_superuser=1 if request.POST.get('permission') == 101 else 0,
                is_staff=1 if request.POST.get('is_staff') else 0,
                is_active=1,
                date_joined=datetime.now()
            )
            user.save()
            user_permission = AuthUserUserPermissions.objects.create(
                user_id=user.id,
                permission_id=request.POST.get('permission')
            )
            log_history(request.user.id, '{} register new user {}.'.format(request.session['first_name'],
                                                                           request.POST.get('fname')))
            message = "Good day, {}! This is an automated message to inform you that this is your account to login " \
                      "in RCStock.net username: {} and password: {}. - The RCStock Management".format(
                request.POST.get('fname'), request.POST.get('uname'), request.POST.get('password1'))
            send_mail(
                'RCStock Account Registration',
                message,
                'support@rcstock.net',
                [request.POST.get('email')]
            )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully created new user.'})
    context = {
        'li_tab': 'users',
        'li': 'employee',
        'tabs_name': 'List of Users',
        'permission': AuthPermission.objects.all()
    }
    return render(request, 'backend/list_of_users.html', context)


@login_required
def view_users(request, pk):
    if request.method == "POST":
        update_users = AuthUser.objects.filter(id=request.POST.get('update-id')).first()
        update_users.username = request.POST.get('uname')
        update_users.first_name = request.POST.get('up_fname')
        update_users.middle_name = request.POST.get('up_mname') if request.POST.get('up_mname') else None
        update_users.last_name = request.POST.get('up_lname')
        update_users.email = request.POST.get('up_email')
        update_users.save()
        log_history(request.user.id, '{} updating the users {}.'.format(request.session['first_name'],
                                                                        request.POST.get('up_fname')))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the user.'})
    subs = TblSubscription.objects.filter(user_id=pk).first()
    context = {
        'users': AuthUser.objects.filter(id=pk).first(),
        'pk': pk,
        'subscription': subs if subs else '',
        'membership_pricing': TblMembershipPricing.objects.filter(is_active=1).order_by('price')
    }
    return render(request, 'backend/view_users.html', context)


@login_required
def assigned_user_roles(request, pk):
    user = AuthUser.objects.filter(id=pk).first()
    if request.method == "POST":
        checked = AuthUserUserPermissions.objects.filter(user_id=pk)
        if checked:
            AuthUserUserPermissions.objects.filter(user_id=pk).update(
                permission_id=request.POST.get('up_permission'))
            log_history(request.user.id, '{} updating the users role of {}.'.format(request.session['first_name'],
                                                                                    user.first_name))
            return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the user roles.'})
        else:
            AuthUserUserPermissions.objects.create(
                user_id=pk,
                permission_id=request.POST.get('up_permission')
            )
            log_history(request.user.id, '{} adding the users role of {}.'.format(request.session['first_name'],
                                                                                  user.first_name))
            return JsonResponse({'data': 'success', 'msg': 'You have successfully adding the user roles.'})

    context = {
        'user_permission': AuthUserUserPermissions.objects.filter(user_id=pk).first(),
        'pk': pk,
        'permission': AuthPermission.objects.all()
    }
    return render(request, 'backend/assigned_user_roles.html', context)


@login_required
@csrf_exempt
def deactivate_users(request):
    AuthUser.objects.filter(id=request.POST.get('id')).update(
        is_active=0
    )
    log_history(request.user.id, '{} deactivate user {}'.format(request.session['first_name'],
                                                                request.POST.get('fullname')))
    return JsonResponse({'data': 'success', 'msg': 'You have successfully deactivated user <strong>{}</strong>'.format(
        request.POST.get('fullname'))})


@login_required
@csrf_exempt
def activate_users(request):
    AuthUser.objects.filter(id=request.POST.get('id')).update(
        is_active=1
    )
    log_history(request.user.id, '{} activate user {}'.format(request.session['first_name'],
                                                              request.POST.get('fullname')))
    return JsonResponse({'data': 'success', 'msg': 'You have successfully activated user <strong>{}</strong>'.format(
        request.POST.get('fullname'))})


@login_required()
@csrf_exempt
def reset_password(request, user_id):
    if request.method == "POST":
        users = AuthUser.objects.filter(id=user_id).first()

        if users.email:
            AuthUser.objects.filter(id=user_id).update(
                password=make_password('rcstock123$')
            )
            message = "Good day, {}! This is an automated message to inform you that your password has been resetted. " \
                      "Your username is {} and your new password is {}. To login, please proceed to this site " \
                      "https://rcstock.net - The RCStock Management".format(users.first_name, users.username,
                                                                            str('rcstock123$'))
            send_mail(
                'RCStock Password Reset',
                message,
                'support@rcstock.net',
                [users.email]
            )
            log_history(request.user.id, '{} resetted account of user {}'.format(request.session['first_name'],
                                                                                 users.first_name))
            return JsonResponse(
                {'data': 'success', 'msg': 'You have successfully resetted account of user <strong>{}</strong>'.format(
                    users.first_name)})
        else:
            return JsonResponse({'error': True, 'msg': 'Unable to reset password due to no emails.'})


@login_required(login_url='sign_in')
def reported_product(request):
    context = {
        'li': 'report_product',
        'tabs_name': 'Reported Product',
    }
    return render(request, 'backend/reported_product.html', context)


@login_required(login_url='sign_in')
def gen_info(request):
    gen_info = TblGeneralInfo.objects.get(id=1)
    if request.method == "POST":
        geninfo = TblGeneralInfo.objects.filter(id=request.POST.get('gen_id')).first()
        geninfo.system_name = request.POST.get('sys_name')
        geninfo.system_version = request.POST.get('system_ver')
        geninfo.address = request.POST.get('address')
        geninfo.mobile_no = request.POST.get('mob_no') if request.POST.get('mob_no') else None
        geninfo.fax = request.POST.get('fax') if request.POST.get('fax') else None
        geninfo.tel_no = request.POST.get('tel_no') if request.POST.get('tel_no') else None
        geninfo.email = request.POST.get('email')
        geninfo.data_protection = request.POST.get('data_protection')
        geninfo.affiliate = request.POST.get('affiliate') if request.POST.get('affiliate') else None
        geninfo.market_intelligence = request.POST.get('market_intelligence') if request.POST.get(
            'market_intelligence') else None
        geninfo.save()
        log_history(request.user.id,
                    '{} updating the general information of the system.'.format(request.session['first_name']))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the general information'})
    context = {
        'li': 'gen_info',
        'tabs_name': 'General Information',
        'li_tab': 'settings',
        'gen_info': gen_info,
        'uploadlogo_form': UploadLogoForm(instance=get_object_or_404(TblGeneralInfo, pk=gen_info.id)),
    }
    return render(request, 'backend/general_information.html', context)


@login_required
def upload_logo_photo(request, pk):
    print('this is ', pk)
    obj = get_object_or_404(TblGeneralInfo, pk=pk)
    form = UploadLogoForm(request.POST, request.FILES, instance=obj)
    if request.method == "POST":
        if form.is_valid():
            picture = form.save(commit=False)
            picture.save()
            form.save()
    return JsonResponse({'data': 'success', 'msg': 'Logo photo was updated.', 'picture': obj.picture.url})


@login_required(login_url='sign_in')
def logs_history(request):
    context = {
        'li': 'logs_history',
        'tabs_name': 'Logs History',
        'li_tab': 'settings'
    }
    return render(request, 'backend/logs_history.html', context)


@login_required(login_url='sign_in')
def membership_pricing(request):
    if request.method == "POST":
        check = TblMembershipPricing.objects.filter(membership_type=request.POST.get('mem_type'))
        if check:
            return JsonResponse({'data': 'error', 'msg': 'Membership type duplicate entry.'})
        else:
            mem = TblMembershipPricing(
                membership_type=request.POST.get('mem_type'),
                duration=request.POST.get('duration'),
                price=request.POST.get('price'),
                services=request.POST.get('services'),
                is_active=1 if request.POST.get('status') else 0,
                uploaded_by_id=request.user.id,
            )
            mem.save()
            log_history(request.user.id, '{} added new membersip pricing {}.'.format(request.session['first_name'],
                                                                                     request.POST.get('mem_type')))
            return JsonResponse({'data': 'success', 'msg': 'You have successfully added new membersip pricing.'})
    context = {
        'li': 'membership_pricing',
        'tabs_name': 'Membership Pricing',
    }
    return render(request, 'backend/membership_pricing.html', context)


@login_required
def update_membership_pricing(request, pk):
    if request.method == "POST":
        update_pricing = TblMembershipPricing.objects.filter(id=pk).first()
        update_pricing.membership_type = request.POST.get('up_mem_type')
        update_pricing.duration = request.POST.get('up_duration')
        update_pricing.price = request.POST.get('up_price')
        update_pricing.services = request.POST.get('up_services')
        update_pricing.is_active = 1 if request.POST.get('up_status') else 0
        update_pricing.save()
        log_history(request.user.id, '{} updating the membersip pricing {}.'.format(request.session['first_name'],
                                                                                    request.POST.get('up_mem_type')))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the membersip pricing.'})
    context = {
        'pricing': TblMembershipPricing.objects.get(id=pk),
        'pk': pk,
    }
    return render(request, 'backend/update_membership_pricing.html', context)


@login_required(login_url='sign_in')
def faq_admin(request):
    if request.method == "POST":
        faq = TblFaq(
            question=request.POST.get('question'),
            answer=request.POST.get('answer'),
            link=request.POST.get('link') if request.POST.get('link') else None,
            created_by_id=request.user.id,
            isactive=1 if request.POST.get('status') else 0,
        )
        faq.save()
        log_history(request.user.id, '{} added new FAQ {}.'.format(request.session['first_name'],
                                                                   request.POST.get('question')))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully added new FAQ.'})
    context = {
        'li': 'faq',
        'tabs_name': 'Frequently Ask Questions',
    }
    return render(request, 'backend/faq.html', context)


@login_required
def update_faq(request, pk):
    if request.method == "POST":
        update_faq = TblFaq.objects.filter(id=pk).first()
        update_faq.question = request.POST.get('up_question')
        update_faq.answer = request.POST.get('up_answer')
        update_faq.link = request.POST.get('up_link')
        update_faq.isactive = 1 if request.POST.get('up_status') else 0
        update_faq.save()
        log_history(request.user.id, '{} updating the FAQ {}.'.format(request.session['first_name'],
                                                                      request.POST.get('up_question')))
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the FAQ.'})
    context = {
        'faq': TblFaq.objects.get(id=pk),
        'pk': pk,
    }
    return render(request, 'backend/update_faq.html', context)

@login_required(login_url='sign_in')
def queries(request):
	context = {
		'li': 'queries',
		'tabs_name': 'Queries',
	}
	return render(request, 'backend/queries.html', context)

@login_required(login_url='sign_in')
def view_queries(request, pk):
    queries = TblContactUs.objects.filter(id=pk).first()
    TblContactUs.objects.filter(id = pk).update(is_seen=1)
    if request.method == "POST":
        TblContactUs.objects.filter(id=pk).update(
            is_reply=1)
        TblContactUsReply.objects.create(
            query_id=pk,
            replied_by_id=request.user.id,
            message=request.POST.get('message'))
        send_mail(
            'RCStock Queries',
            request.POST.get('message'),
            'support@rcstock.net',
            [queries.email],
            html_message=request.POST.get('message')
        )
        return JsonResponse({'data': 'success', 'msg': 'You have successfully replied customers queries.'})
    context = {
        'queries': queries,
        'pk': pk
    }
    return render(request, 'backend/view_queries.html', context)
# TO BE CODED
# def activate_user(request, uidb64, token):
#     generate_token = TokenGenerator()
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#
#         user = User.objects.get(pk=uid)
#
#     except Exception as e:
#         user = None
#
#     if user and generate_token.check_token(user, token):
#         user.is_email_verified = True
#         user.save()
#
#         messages.add_message(request, messages.SUCCESS,
#                              'Email verified, you can now login')
#         return redirect(reverse('login'))
#
#     return render(request, 'backend/email_temp/activate-failed.html', {"user": user})
