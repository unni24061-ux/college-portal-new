from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from . models import faculty_profile



# Create your views here.
@login_required(login_url='login_p')
def dashboard(request):
    return render(request,'faculty/faculty_dash.html')

def f_profile(request):
    profile = faculty_profile.objects.get(user=request.user)
    return render(request,'faculty/faculty_myprofile.html',{'profile':profile})


@login_required(login_url='login_p')
def f_edit_profile(request):

    profile = faculty_profile.objects.get(user=request.user)

    if request.method == "POST":

        profile.fullname = request.POST.get("fullname")
        profile.department = request.POST.get("department")
        profile.designation = request.POST.get("designation")
        profile.ph_no = request.POST.get("phone_number")
        profile.save()

        email = request.POST.get("email")
        if email:
            request.user.email = email
            request.user.save()

        return redirect("facu_profile")

    return redirect("facu_profile")