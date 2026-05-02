from django.contrib import admin
from .models import Category, CategoryFilter, CategorySEOKeyword
# Register your models here.
admin.site.register(Category)
admin.site.register(CategoryFilter)
admin.site.register(CategorySEOKeyword)