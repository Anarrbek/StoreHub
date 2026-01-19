from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<str:slug>/', views.product_detail, name='product_detail'),
    path('add-product/', views.add_product, name='add_product'),
    path('product-create/', views.add_product, name='product_create'),
    path('rules/', views.rules, name='rules'),
    path('faq/', views.faq, name='faq'),
    path('theme/', views.theme_main, name='theme_main'),
    
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update_quantity, name='cart_update'),
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/confirm/<int:order_id>/', views.order_confirm, name='order_confirm'),
    
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('cart/restore/<int:item_id>/', views.cart_restore, name='cart_restore'),
    
    path('favorites/', views.favorites_list, name='favorites'),
    path('favorites/add/<int:product_id>/', views.fav_add, name='fav_add'),
    path('favorites/remove/<int:product_id>/', views.fav_remove, name='fav_remove'),
  
    path('products/<int:product_id>/review/', views.review_add, name='review_add'),
    path('products/<int:product_id>/reserve/', views.reserve_view, name='reserve'),
    path('products/<int:product_id>/buy/', views.buy_now, name='buy_now'),
    
    path('reservations/', views.reservations_list, name='reservations'),
    path('reservations/<int:res_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),

    path('search/', views.search_view, name='search'),
]
