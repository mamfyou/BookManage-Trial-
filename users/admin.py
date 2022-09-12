from django.contrib import admin
from .models import *


@admin.register(BookUser)
class BookUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'telegram_id')
    list_filter = ('username', 'phone_number', 'telegram_id')
    search_fields = ('username', 'email', 'phone_number', 'telegram_id')
    ordering = ('id',)
