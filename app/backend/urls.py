from django.urls import path

from app.backend.views import sign_in, dashboard, registration, list_of_shop, update_shop, list_of_users, \
    reported_product, list_of_suppliers, logs_history, sign_out, list_of_shop_scrapper, update_shop_scrapper, gen_info, \
    upload_logo_photo, upload_shoplogo, view_users, assigned_user_roles, deactivate_users, activate_users, \
    reset_password, \
    membership_pricing, update_membership_pricing, faq_admin, update_faq, queries, view_queries

urlpatterns = [
    path('', sign_in, name='sign_in'),
    path('sign-out/', sign_out, name='sign_out'),
    path('dashboard/', dashboard, name='dashboard'),
    path('registration/', registration, name='registration'),
    path('shop/scrapper/', list_of_shop_scrapper, name='list_of_shop_scrapper'),
    path('shop/update/scrapper/<int:pk>', update_shop_scrapper, name='update_shop_scrapper'),
    path('shop/list/', list_of_shop, name='list_of_shop'),
    path('shop/update/<int:pk>', update_shop, name='update_shop'),
    path('users/list/', list_of_users, name='list_of_users'),
    path('update-users-list/<int:pk>', view_users, name='view_users'),
    path('assigned-users-roles/<int:pk>', assigned_user_roles, name='assigned_user_roles'),
    path('deactivate_users/', deactivate_users, name='deactivate_users'),
    path('activate_users/', activate_users, name='activate_users'),
    path('reset_password/<int:user_id>', reset_password, name='reset_password'),
    path('reported_product/', reported_product, name='reported_product'),
    path('list_of_suppliers/', list_of_suppliers, name='list_of_suppliers'),
    path('logs_history/', logs_history, name='logs_history'),
    path('general-information/', gen_info, name='gen_info'),
    path('update-system-logo/<int:pk>', upload_logo_photo, name='upload_logo_photo'),
    path('update-shops-logo/<int:pk>', upload_shoplogo, name='upload_shoplogo'),
    path('membership/pricing/', membership_pricing, name='membership_pricing'),
    path('update/membership/pricing/<int:pk>', update_membership_pricing, name='update_membership_pricing'),
    path('frequently-ask-questions/', faq_admin, name='faq_admin'),
    path('update/frequently-ask-questions/<int:pk>', update_faq, name='update_faq'),
    path('queries/', queries, name='queries'),
    path('view/queries/<int:pk>', view_queries, name='view_queries'),
    #    path('activate_user/<uidb64>/<token>', activate_user, name='activate'),
]
