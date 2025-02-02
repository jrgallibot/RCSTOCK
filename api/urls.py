from django.urls import path

from api.shops.views import ShopView, ScrappperView
from api.users.views import UserlistView, SuppliersView
from api.settings.views import LogsView
from api.membership_pricing.views import MembershipPricingView
from api.views import FaqView, QueriesView

urlpatterns = [
    path('shop/', ShopView.as_view(), name='api_shop'),
    path('shop/scrapper/', ScrappperView.as_view(), name='api_shop_scrapper'),
    path('users/', UserlistView.as_view(), name='api_users'),
    path('suppliers/', SuppliersView.as_view(), name='api_suppliers'),
    path('logs/', LogsView.as_view(), name='api_logs'),
    path('memship_pricing/', MembershipPricingView.as_view(), name='api_memship_pricing'),
    path('faq/', FaqView.as_view(), name='api_faq'),
    path('queries/', QueriesView.as_view(), name='api_queries'),
]
