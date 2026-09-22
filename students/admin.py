from django.contrib import admin

from .models import student_profile


@admin.register(student_profile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'roll_no', 'department', 'sem')
    search_fields = ('user__username', 'fullname', 'roll_no', 'department')
    list_filter = ('department', 'sem')
    readonly_fields = ('user',)