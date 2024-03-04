from django.contrib import admin

# Register your models here.
from .models import ChatBody

class ChatBodyAdmin(admin.ModelAdmin):
    list_display = ['id', 'use_context', 'include_sources', 'stream']  # Adjust fields as needed
    search_fields = ['id']  # Add fields you want to search by
    list_filter = ['use_context', 'stream']  # Add fields you want to filter by

admin.site.register(ChatBody, ChatBodyAdmin)