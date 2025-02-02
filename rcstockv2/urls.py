from django.conf.urls.static import static
from django.urls import path, include

from app.cron.in_stock_notif import in_stock_notif
from app.paypal import views
from app.paypal.views import process_payment
from app.views import landing, autocomplete_suggestions, about, data_protection, \
    login_user, logout_user, contact_us, user_dashboard, user_changepassword, \
    user_account, affiliate, market_intelligence, product_click, get_in_stock, get_all_stock, search_results_v2, \
    process_search_results_v2, user_market_intelligence_dashboard, user_market_intelligence_shops, \
    faq, notify_me, subscribe_free, price_development
from rcstockv2 import settings

urlpatterns = [
    path('', landing, name='landing'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('contact/', contact_us, name='contact_us'),
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('user/market-intelligence/dashboard/', user_market_intelligence_dashboard,
       name='user_market_intelligence_dashboard'),
    path('user/market-intelligence/shop/<int:pk>/<int:owner_id>', user_market_intelligence_shops,
       name='user_market_intelligence_shops'),
    path('user/changepassword/', user_changepassword, name='user_changepassword'),
    path('user/account/', user_account, name='user_account'),
    path('autocomplete/', autocomplete_suggestions, name='autocomplete_suggestions'),
    path('shop/search/results/process/<str:search_input>/<int:pk>/<int:beta_search>',
       process_search_results_v2,
       name='process_search_results'),
    path('shop/search/results/<str:search_input>/<int:pk>/<int:beta_search>', search_results_v2,
       name='search_results'),
    path('shop/products/notify/', in_stock_notif, name='in_stock_notif'),
    path('shop/search/results/process/in-stock/<str:search_input>/<int:pk>/<int:beta_search>',
       get_in_stock,
       name='get_in_stock'),
    path('shop/search/results/process/all-stock/<str:search_input>/<int:pk>/<int:beta_search>',
       get_all_stock,
       name='get_all_stock'),
    path('shop/product/click/<int:pk>', product_click, name='product_click'),
    path('about/', about, name='about'),
    path('affiliate/', affiliate, name='affiliate'),
    path('frequently-ask-questions/', faq, name='faq'),
    path('market_intelligence/', market_intelligence, name='market_intelligence'),
    # path('subscribe-paypal/<int:pk>/<int:user_id>', subscribe_paypal, name='subscribe_paypal'),
    path('data/protection/', data_protection, name='data_protection'),
    path('rc-admin/', include('app.backend.urls')),
    path('api/', include('api.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal/subscribe/<int:pk>/<int:user_id>', process_payment, name='subscribe_paypal'),
    path('paypal/subscribe/success/', views.payment_done, name='payment_done'),
    path('paypal/subscribe/cancelled/', views.payment_canceled, name='payment_cancelled'),
    path('shop/product/notify/', notify_me, name='notify_me'),
    path('subscribe/free/', subscribe_free, name='subscribe_free'),
    path('price/development/<str:prod_name>', price_development, name='price_development'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
