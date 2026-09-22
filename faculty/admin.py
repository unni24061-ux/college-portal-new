from django.contrib import admin

from .models import Announcement, faculty_profile


@admin.register(faculty_profile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'designation', 'department', 'is_approved')
    search_fields = ('user__username', 'fullname', 'designation', 'department')
    list_filter = ('is_approved', 'department')
    list_editable = ('is_approved',)
    readonly_fields = ('user',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'message', 'created_by__username')
    readonly_fields = ('created_by', 'created_at')