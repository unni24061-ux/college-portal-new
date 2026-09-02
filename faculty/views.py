from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from . models import faculty_profile, Announcement
from students.models import student_profile
from django.contrib import messages
from django.db.models import Q



# Create your views here.
@login_required(login_url='login_p')
def dashboard(request):
    return render(request,'faculty/faculty_dash.html')

@login_required(login_url='login_p')
def f_profile(request):
    profile = faculty_profile.objects.get(user=request.user)
    return render(request,'faculty/faculty_myprofile.html',{'profile':profile})


@login_required(login_url='login_p')
def f_edit_profile(request):

    profile = faculty_profile.objects.get(user=request.user)

    if request.method == "POST":

        fullname = request.POST.get("fullname")
        if profile:
            profile.fullname=fullname
        
        
        
        department = request.POST.get("department")
        if department:
            profile.department=department
        else:
            profile.department=None

        designation = request.POST.get("designation")
        if designation:
            profile.designation=designation
        else:
            profile.designation=None

        ph_no = request.POST.get("phone_number")
        if ph_no:
            profile.ph_no=ph_no
        else:
            profile.ph_no=None

        if request.FILES.get("profile_image"):
            profile.profile_image=request.FILES.get("profile_image")
        profile.save()

        email = request.POST.get("email")
        if email:
            request.user.email = email
            request.user.save()

        messages.success(request, "Profile updated successfully!")

        return redirect("facu_profile")

    return redirect("facu_profile")

@login_required(login_url='login_p')
def stud_manage(request):
    students = student_profile.objects.all()

    search=request.GET.get('search','').strip()
    if search :
        students = students.filter(
            Q(fullname__icontains=search)|
            Q(roll_no__icontains=search)|
            Q(user__email__icontains=search)|
            Q(department__iexact=search)|
            Q(ktu_id__icontains=search)

        )

    department=request.GET.get('department')
    if department:
        students=students.filter(department__iexact=department)

    sem=request.GET.get('sem')
    if sem:
        students=students.filter(sem=sem)
    return render(request,'faculty/student_manage.html',{'students':students})



@login_required(login_url='login_p')
def preview(request,id):
    student=student_profile.objects.get(id=id)

    return render(request,'faculty/preview_pro.html',{'student':student})

@login_required(login_url='login_p')
def edit_pro_f(request, id):

    profile = student_profile.objects.get(id=id)

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
            profile.department = ""

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

        return redirect("preview", id=id)

    return redirect("preview", id=id)

@login_required(login_url='login_p')

def campus_connect(request,role,id):



    role=request.GET.get('role')



    if role == ('faculty'):

        directory = faculty_profile.objects.all()

    else:

        directory= student_profile.objects.all()

   

    search=request.GET.get('search','').strip()

    if search :

        directory = directory.filter(

            Q(fullname__icontains=search)|

            Q(roll_no__icontains=search)|

            Q(user__email__icontains=search)|

            Q(department__iexact=search)|

            Q(ktu_id__icontains=search)



        )



    department=request.GET.get('department')

    if department:

        directory=directory.filter(department__iexact=department)



    sem=request.GET.get('sem')

    if sem:

        directory=directory.filter(sem=sem)

    return render(request,'faculty/campus_connect.html',{'directory':directory,'role':role})


@login_required(login_url='login_p')
def announcement(request):

    if request.method == "POST":

        title = request.POST.get("title")
        message = request.POST.get("message")

        if title and message:

            Announcement.objects.create(
                title=title,
                message=message,
                created_by=request.user
            )

            messages.success(
                request,
                "Announcement published successfully!"
            )

            return redirect("f_notification")

    return render(request, 'faculty/announcement.html')


@login_required(login_url='login_p')
def notification(request):

    announcements = Announcement.objects.all().order_by(
        '-created_at'
    )

    return render(
        request,
        'faculty/notification.html',
        {
            'announcements': announcements
        }
    )