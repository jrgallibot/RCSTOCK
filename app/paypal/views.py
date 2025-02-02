import random
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from app.backend.models import TblMembershipPricing, TblSubscription
from app.models import AuthUser
from app.paypal.forms import ExtPayPalPaymentsForm


def generate_invoice():
    return str('{}-{}'.format('%4x' % random.getrandbits(2 * 8), '%8x' % random.getrandbits(4 * 8))).upper()


def process_payment(request, pk, user_id):
    user = AuthUser.objects.filter(id=user_id)
    membership = TblMembershipPricing.objects.filter(Q(is_active=1) & Q(id=pk)).first()
    host = request.get_host()

    invoice = generate_invoice()
    while TblSubscription.objects.filter(invoice=invoice).first() is not None:
        invoice = generate_invoice()

    sub = TblSubscription.objects.create(
        user_id=user_id,
        membership_id=pk,
        created_at=datetime.now(),
        status=0,
        invoice=invoice
    )

    request.session['paypal_user_email'] = user.first().email
    request.session['paypal_subscription_id'] = sub.id

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % membership.price.quantize(Decimal('.01')),
        'item_name': '{} MEMBERSHIP'.format(str(membership.membership_type).upper()),
        'invoice': invoice,
        'currency_code': settings.PAYPAL_CURRENCY,
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')),
    }

    form = ExtPayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'paypal/form.html', {
        'form': form,
        'mem': membership,
        'pk': pk,
        'user_id': user_id
    })


@csrf_exempt
def payment_done(request):
    try:
        sub = TblSubscription.objects.filter(id=request.session['paypal_subscription_id'])
        TblSubscription.objects.filter(user_id=sub.first().user_id).update(status=0)
        sub.update(status=1)

        message = "Thank you for your {} subscription worth ${}/month in RCStock.net " \
                  "- The RCStock Management".format(str(sub.first().membership.membership_type).upper(),
                                                    sub.first().membership.price)
        send_mail(
            'RCStock Subscription',
            message,
            'support@rcstock.net',
            [request.session['paypal_user_email']]
        )
    except Exception as e:
        print(e)

    del request.session['paypal_user_email']
    del request.session['paypal_subscription_id']
    request.session['paypal_payment_title'] = 'Subscription Paid'
    request.session['paypal_payment_status'] = 'success'
    request.session['paypal_payment_message'] = 'You have successfully subscribed to RCStock. Thank you!'
    return redirect('login_user')


@csrf_exempt
def payment_canceled(request):
    request.session['paypal_payment_title'] = 'Subscription Cancelled'
    request.session['paypal_payment_status'] = 'error'
    request.session['paypal_payment_message'] = 'You have cancelled your subscription transaction. ' \
                                                'You may try again later.'
    return redirect('market_intelligence')
