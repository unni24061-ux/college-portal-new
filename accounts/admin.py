from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuditLog, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    fieldsets = UserAdmin.fieldsets + (('Portal Role', {'fields': ('role',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Portal Role', {'fields': ('role',)}),)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'target_type', 'target_id', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('actor__username', 'action', 'detail')
    readonly_fields = ('actor', 'action', 'target_type', 'target_id', 'detail', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False