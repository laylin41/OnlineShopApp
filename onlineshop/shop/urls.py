from django.urls import path

#now import the views.py file into this code
from . import views

urlpatterns=[
path('', views.index, name='home'),
path('register/', views.register, name='register'),
path('login/', views.login, name='login'),
path('logout/', views.logout, name='logout'),
path('profile/', views.profile, name='profile'),
path('profile/change-password/', views.change_password, name='change_password'),
path('category/<int:category_id>/', views.category_show, name='category_show'),
path('categories/', views.all_categories_show, name='all_categories_show'),

path('goods/<int:good_id>/', views.goods_detail, name='goods-detail'),
path('reviews/delete/<int:review_id>/', views.delete_review, name='delete-review'),

path('cart/add/<int:good_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/show', views.cart_view, name='cart_view'),
path('cart/remove/<int:good_id>/', views.remove_from_cart, name='remove_from_cart'),
path('checkout/', views.checkout, name='checkout'),
path('history/', views.orders_history, name='orders_history')
]
