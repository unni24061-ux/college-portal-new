from django.contrib import admin

from .models import Attendance, AttendanceSession, Course, Department, Grade, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'duration_sems')
    list_filter = ('department',)
    search_fields = ('name', 'code')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'course', 'sem', 'credits')
    list_filter = ('course', 'sem')
    search_fields = ('name', 'code')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'sem', 'grade', 'marks', 'updated_at')
    list_filter = ('sem', 'grade')
    search_fields = ('student__fullname', 'student__roll_no', 'subject__code')


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'started_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'subject', 'started_at')
    readonly_fields = ('token', 'token_bucket')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_at')
    list_filter = ('status', 'marked_at', 'session__subject')
    search_fields = ('student__fullname', 'student__roll_no')