import html
from datetime import date

import urllib3
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.html import strip_tags
from selectolax.parser import HTMLParser

from app.models import Products, ShopScraperAdditional
from app.views import string_validator, stock_status_validator


def in_stock_notif(request):
    today = date.today()
    products = Products.objects.filter(date_search__lt=today).all()

    if products:
        for product in products:
            scraper = ShopScraperAdditional.objects.filter(shop_id=product.shop_id).first()
            http = urllib3.PoolManager()
            r = http.request('GET', html.unescape(product.link))
            soup = HTMLParser(r.data.decode('utf-8'))

            try:
                lines = soup.css(str(scraper.wrapper))
            except Exception as e:
                lines = None

            if lines:
                for line in lines:
                    stock_status = line.css_first(str(scraper.stock_status)) if scraper.stock_status else None
                    stock_status = stock_status_validator(product.shop_id, string_validator(stock_status)) \
                        if stock_status else stock_status_validator(product.shop_id, None)

                    prod = Products.objects.filter(id=product.id)
                    old_product_status = product.stock_status
                    message = None
                    if stock_status.strip() == 'In Stock':
                        if old_product_status != 'In Stock':
                            prod.update(stock_status='In Stock')
                            message = 'This item: <strong>{}</strong> is now in stock and can now be purchased. ' \
                                      'Please visit: <strong>{}</strong> to do so. - The RCStock Management'.format(
                                product.product_name, product.link)
                    else:
                        if old_product_status != 'Out of Stock':
                            prod.update(stock_status='Out of Stock')
                            message = 'This item: <strong>{}</strong> has now become out of stock. ' \
                                      'We will continue to monitor this item and update you when it is now in stock ' \
                                      'again. You may also visit the product through this link: <strong>{}</strong>. ' \
                                      '- The RCStock Management'.format(
                                product.product_name, product.link)

                    prod.update(date_search=today)
                    if message:
                        send_mail(
                            'RCStock Notification Subscription',
                            strip_tags(message),
                            'support@rcstock.net',
                            [product.email],
                            html_message=message
                        )

    return JsonResponse({'data': 'success'})
