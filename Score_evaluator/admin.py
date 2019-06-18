from django.contrib import admin
from .models import Category, CategoryScore


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
    list_display = ("id", "name", "parent")


@admin.register(CategoryScore)
class CategoryScoreAdmin(admin.ModelAdmin):
    search_fields = ["user", "category"]
    list_display = ("user", "category", "likes", "real_value")
