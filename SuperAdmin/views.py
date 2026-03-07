import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from SuperAdmin.models import CollegeDb, EventDb
from django.contrib.auth.models import User
from django.contrib.auth import  authenticate,login
from django.views.decorators.csrf import csrf_exempt
from WebApp.models import RegistrationDb


# Create your views here.
def SuperAdminPanel(request):
    return render(request,'super_admin.html')
def AddCollege(request):
    return render(request,'add_college.html')
def ViewCollege(request):
    college = CollegeDb.objects.all()
    return render(request,'view_college.html',{'college':college})
def Save_college(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        website = request.POST.get('web')
        mobile = request.POST.get('mob')
        logo = request.FILES['logo']
        cuname = request.POST.get('college_uname')
        cpswd = request.POST.get('college_pswd')
        obj = CollegeDb(name=name,address=address,email=email,web=website,mob=mobile,logo=logo,cuname=cuname,cpswd=cpswd)
        obj.save()
        return redirect(AddCollege)
def delete_college(request,college_id):
    college = CollegeDb.objects.filter(id=college_id)
    college.delete()
    return redirect(ViewCollege)
def EditCollege(request,college_id):
    college = CollegeDb.objects.get(id=college_id)
    return render(request,'edit_college.html',{'college':college})
def update_college(request,college_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        website = request.POST.get('web')
        mobile = request.POST.get('mob')
        cuname = request.POST.get('college_uname')
        cpswd = request.POST.get('college_pswd')
        try:
            logo = request.FILES['logo']
            fs = FileSystemStorage()
            file = fs.save(logo.name,logo)
        except MultiValueDictKeyError:
            file = CollegeDb.objects.get(id=college_id).logo
        CollegeDb.objects.filter(id=college_id).update(name=name,address=address,email=email,web=website,mob=mobile,logo=file,cuname=cuname,cpswd=cpswd)
        return redirect(ViewCollege)

def login_page(request):
    return render(request,'login_page.html')

def admin_login(request):
    if request.method == "POST":
        uname = request.POST.get('username')
        pswd = request.POST.get('password')
    if User.objects.filter(username__contains=uname).exists():
        user = authenticate(username=uname,password=pswd)
        if user is not None:
            login(request, user)
            request.session['username'] = uname
            request.session['password'] = pswd
            return redirect(SuperAdminPanel)
        else:
            print("Invalid Details..!")
            return redirect(login_page)
    elif CollegeDb.objects.filter(cuname=uname, cpswd=pswd).exists():
        request.session['username'] = uname
        request.session['password'] = pswd
        return redirect(CollegeAdminPanel)
    else:
        print("User not found..!")
        return redirect(login_page)

def admin_logout(request):
    del request.session['username']
    del request.session['password']
    return redirect(login_page)

def CollegeAdminPanel(request):
    return render(request,'college_admin.html')

def AddEvent(request):
    return render(request,'add_event.html')
def Save_event(request):
    if request.method == "POST":
        euname = request.POST.get('euname')
        title = request.POST.get('title')
        desc = request.POST.get('description')
        type = request.POST.get('type')
        dept = request.POST.get('dept')
        start = request.POST.get('start')
        end = request.POST.get('end')
        dead = request.POST.get('dead')
        mode = request.POST.get('mode')
        loc = request.POST.get('location')
        maxS = request.POST.get('maxS')
        fee = request.POST.get('fee')
        certify = request.FILES['certificate']
        poster = request.FILES['poster']
        obj = EventDb(euname=euname,title=title,description=desc,type=type,dept=dept,start=start,end=end,dead=dead,mode=mode,location=loc,maxS=maxS,fee=fee,certificate=certify,poster=poster)
        obj.save()
        return redirect(AddEvent)
def view_event(request):
    uname = request.session.get('username')
    own_event = EventDb.objects.filter(euname=uname)
    return render(request,'view_event.html',{'own_event':own_event})

def all_event(request):
    allEvent = EventDb.objects.all()
    return render(request,'event_approval.html',{'allEvent':allEvent})

def event_approval(request,approval_id):
    if request.method == "POST":
        event = EventDb.objects.get(id=approval_id)
        event.status = "Approved"
        event.save()
        return redirect(all_event)
def delete_event(request,delete_id):
    event = EventDb.objects.filter(id=delete_id)
    event.delete()
    return redirect(view_event)

def college_registered_events(request):
    uname = request.session.get('username')
    event = EventDb.objects.filter(euname=uname)
    return render(request,'view_registrations.html',{'event':event})

def student_registrations(request,viewreg_id):
    event = EventDb.objects.filter(id=viewreg_id)
    eventname = EventDb.objects.get(id=viewreg_id)
    registered = RegistrationDb.objects.filter(event_name=eventname.title)
    return render(request,'student_registrations.html',{
        'event':event,
        'registered':registered
    })
def delete_register(request,delete_id):
    registered = RegistrationDb.objects.filter(id=delete_id)
    registered.delete()
    return redirect(college_registered_events)

def QrScanPage(request):
    return render(request,'college_qrscan.html')

@csrf_exempt
def process_qr(request):
    if request.method == "POST":
        data = json.loads(request.body)
        s_name = data.get("name")
        s_email = data.get("email")
        s_mob = data.get("mobile")
        s_event = data.get("event")
        print(s_name,s_email,s_mob,s_event)
        RegistrationDb.objects.filter(
            sname = s_name,
            semail = s_email,
            smob = s_mob,
            event_name = s_event
        ).update(sattendance="Present")

        return HttpResponse(status=204)



