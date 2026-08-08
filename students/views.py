from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *

# Create your views here.
@login_required(login_url='login_p')
def dashboard(request):
    return render(request,'students/student_dash.html')

@login_required(login_url='login_p')
def s_profile(request):
    profile = student_profile.objects.get(user=request.user)
    return render(request,'students/stud_myprofile.html',{'profile':profile})

@login_required(login_url='login_p')
def edit_profile(request):

    profile = student_profile.objects.get(user=request.user)

    if request.method == "POST":

        profile.fullname = request.POST.get("fullname")
        profile.department = request.POST.get("department")
        profile.ktu_id = request.POST.get("ktu_id")
        profile.ph_no = request.POST.get("ph_no")
        profile.roll_no = request.POST.get("roll_no")
        profile.dob = request.POST.get("dob")
        profile.cgpa = request.POST.get("cgpa")

        profile.save()

        return redirect("stud_profile")

    return redirect("stud_profile")