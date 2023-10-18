# admin.py
from django.contrib import admin
from .models import IssueRequest, IssuedBook


@admin.register(IssueRequest)
class IssueRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'volume_id', 'user', 'requested_at')


@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'volume_id', 'user', 'issued_at')
