from django.contrib import admin
from django.urls import path
from blogs_app import views
from django.conf.urls.static import static 
from django.conf import settings

urlpatterns = [
    path('home', views.blogHome, name = 'blogHome') ,
    path('<str:slug>/', views.blog, name = 'blog') , 
    path('create_blog', views.create_blog, name='create_blog') ,
    path('search' , views.search , name='search') ,
    path('edit_post/<str:slug>/', views.edit_post, name='edit_post'),
    path('post_comment', views.post_comment, name='post_comment'),
    path('delete_post/<str:slug>/', views.delete_post, name='delete_post'),
    path('delete_comment/<int:id>/', views.delete_comment, name='delete_comment'),
]