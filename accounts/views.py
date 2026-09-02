from django.shortcuts import render, redirect
from .forms import createuserform
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from students.models import student_profile
from faculty.models import faculty_profile
from django.contrib.auth.decorators import login_required


# Student Registration
def stud_reg(request):
    if request.method == 'POST':
        form = createuserform(request.POST)

        if form.is_valid():
            user = form.save()

            student_profile.objects.create(
                user=user
            )

            messages.success(request, "Student registered successfully.")
            return redirect('login_p')

        else:
            messages.error(request, "Registration failed. Please correct the errors below.")

    else:
        form = createuserform()

    return render(request, 'accounts/studreg.html', {'form': form})


# Faculty Registration
def faculty_reg(request):
    if request.method == 'POST':
        form = createuserform(request.POST)

        if form.is_valid():
            user = form.save()

            faculty_profile.objects.create(
                user=user
            )

            messages.success(request, "Faculty registered successfully.")
            return redirect('pend_page')

        else:
            messages.error(request, "Registration failed. Please correct the errors below.")

    else:
        form = createuserform()

    return render(request, 'accounts/facultyreg.html', {'form': form})


# Login
def login_page(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:

            login(request, user)
            messages.success(request, "Login successful.")

            if student_profile.objects.filter(user=user).exists():
                messages.success(request,"Succesfully logged in")
                return redirect('stud_dash')

            elif faculty_profile.objects.filter(user=user).exists():
                faculty=faculty_profile.objects.get(user=user)
                if not faculty.is_approved:
                    messages.warning(
                        request,"your account is not verified"
                    )
                    return redirect('pend_page')
                login(request,user)
                messages.success(request,"Successfully logged in")
                return redirect('facu_dash')

            else:
                messages.error(request, "Profile not found.")
                logout(request)

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')

def logout_page(request):

    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login_p')

def pending(request):
    return render(request,'accounts/pending.html')