from django.contrib import admin
from django.urls import path
from home_app import views
from blogs_app import urls

urlpatterns = [
    path('', views.home, name = 'home') ,
    path('about', views.about, name = 'about') ,
    path('contact', views.contact, name = 'contact') ,
    path('login', views.login_function, name = 'login') , 
    path('signup', views.signup, name = 'signup') ,
    path('logout', views.logoutUser, name = 'logout') , 
    path('forgot_password', views.forgot_password, name='forgot_password')
]