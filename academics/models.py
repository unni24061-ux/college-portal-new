from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    duration_sems = models.PositiveSmallIntegerField(default=8)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    sem = models.PositiveSmallIntegerField()
    credits = models.PositiveSmallIntegerField(default=4)

    class Meta:
        ordering = ('sem', 'code')
        unique_together = ('course', 'code')

    def __str__(self):
        return f"{self.name} ({self.code})"


class Grade(models.Model):
    GRADE_CHOICES = [
        ('S', 'S'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    student = models.ForeignKey(
        'students.student_profile',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    sem = models.PositiveSmallIntegerField()
    marks = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'sem')
        ordering = ('subject__code',)

    def __str__(self):
        return f"{self.student} · {self.subject.code} · {self.grade}"


class AttendanceSession(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    token = models.CharField(max_length=100, blank=True, default="")
    token_bucket = models.BigIntegerField(default=0)

    class Meta:
        ordering = ('-started_at',)

    def __str__(self):
        return f"{self.subject.code} session #{self.pk}"

    def is_live(self):
        return self.is_active and self.closed_at is None


class Attendance(models.Model):
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records'
    )
    student = models.ForeignKey(
        'students.student_profile',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    status = models.CharField(
        max_length=10,
        choices=[('present', 'Present'), ('late', 'Late')],
        default='present'
    )
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')
        ordering = ('-marked_at',)

    def __str__(self):
        return f"{self.student} · {self.session.subject.code} · {self.status}"