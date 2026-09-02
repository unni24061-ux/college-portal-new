from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages

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

        # Full Name
        fullname = request.POST.get("fullname", "").strip()

        if fullname:
            profile.fullname = fullname

        # Department
        department = request.POST.get("department", "").strip()

        if department:
            profile.department = department
        else:
            profile.department = None

        # Semester
        sem = request.POST.get("sem", "").strip()

        if sem in ("", "None", "null"):
            profile.sem = None
        else:
            profile.sem = int(sem)

        # KTU ID
        ktu_id = request.POST.get("ktu_id", "").strip()

        if ktu_id:
            profile.ktu_id = ktu_id
        else:
            profile.ktu_id = None

        # Phone Number
        ph_no = request.POST.get("ph_no", "").strip()

        if ph_no:
            profile.ph_no = ph_no
        else:
            profile.ph_no = None

        # Roll Number
        roll_no = request.POST.get("roll_no", "").strip()

        if roll_no in ("", "None", "null"):
            profile.roll_no = None
        else:
            profile.roll_no = int(roll_no)

        # Date of Birth
        dob = request.POST.get("dob", "").strip()

        if dob:
            profile.dob = dob
        else:
            profile.dob = None

        # CGPA
        cgpa = request.POST.get("cgpa", "").strip()

        if cgpa in ("", "None", "null"):
            profile.cgpa = None
        else:
            profile.cgpa = float(cgpa)

        # Profile Image
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect("stud_profile")

    return redirect("stud_profile")