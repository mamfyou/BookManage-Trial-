from django.contrib import admin
from book.models import *


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'publish_date', 'page_count', 'picture')


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
