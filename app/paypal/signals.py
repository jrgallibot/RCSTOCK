from django.conf import settings
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from app.backend.models import TblSubscription


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == ST_PP_COMPLETED:
        # You need to check the amount received,
        # `custom` etc. are all what you expect or what
        # is allowed.
        try:
            invoice = ipn.invoice
            subscription = TblSubscription.objects.get(invoice=invoice)
            assert ipn.mc_gross == subscription.membership.price and ipn.mc_currency == settings.PAYPAL_CURRENCY
        except Exception as e:
            print(e)
        else:
            subscription.status = True
            subscription.save()
    else:
        print('Paypal payment status not completed: %s' % ipn.payment_status)
