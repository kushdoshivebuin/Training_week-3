from django.contrib import admin
from blogs_app.models import Post, BlogComment
# Register your models here.

admin.site.register((Post, BlogComment))