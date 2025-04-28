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
]
