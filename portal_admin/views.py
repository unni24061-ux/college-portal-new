from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from faculty.models import faculty_profile


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin, login_url='/admin/login/')
def admin_dashboard(request):

    pending_faculty = faculty_profile.objects.filter(
        is_approved=False
    )

    approved_faculty = faculty_profile.objects.filter(
        is_approved=True
    )

    return render(
        request,
        'portal_admin/dashboard.html',
        {
            'pending_faculty': pending_faculty,
            'approved_faculty': approved_faculty,
        }
    )

@user_passes_test(is_admin, login_url='/admin/login/')
def approve_faculty(request, id):

    faculty = faculty_profile.objects.get(id=id)

    faculty.is_approved = True
    faculty.save()

    messages.success(
        request,
        f"{faculty.user.username} has been approved."
    )

    return redirect('admin_dashboard')

@user_passes_test(is_admin, login_url='/admin/login/')
def reject_faculty(request, id):

    faculty = faculty_profile.objects.get(id=id)

    faculty.is_approved = False
    faculty.save()

    messages.error(
        request,
        f"{faculty.user.username} has been rejected."
    )

    return redirect('admin_dashboard')