from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class faculty_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    ph_no = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images',
        default='default.png',
        blank=True,
    )
    is_approved = models.BooleanField(default=False)


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title