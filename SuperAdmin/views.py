import json
import os
from django.contrib import messages
from django.db.models import Sum,Count,Q
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from SuperAdmin.models import DepartmentDb, EventDb
from django.contrib.auth.models import User
from django.contrib.auth import  authenticate,login
from django.views.decorators.csrf import csrf_exempt
from WebApp.models import RegistrationDb


# Create your views here.
def SuperAdminPanel(request):
    #College cards
    total_reg = RegistrationDb.objects.count()
    total_event = EventDb.objects.count()
    approve_event = EventDb.objects.filter(status="Approved").count()
    pending_event = EventDb.objects.filter(status="Pending").count()
    paid_revenue = RegistrationDb.objects.filter(pay_status="Paid").aggregate(total=Sum('fee'))['total'] or 0
    unpaid_revenue = RegistrationDb.objects.filter(pay_status="Unpaid").aggregate(total=Sum('fee'))['total'] or 0
    attended = RegistrationDb.objects.filter(sattendance="Present").count()
    percent = round((attended / total_reg * 100), 2) if total_reg else 0

    #Departments Chart
    dept_data = RegistrationDb.objects.values('dept_name').annotate(
        total_reg=Count('id'),
        paid_reg=Count('id', filter=Q(pay_status='Paid')),
        total_revenue=Sum('fee', filter=Q(pay_status='Paid'))
    )
    labels = []
    registrations = []
    revenue = []
    paid_reg = []
    for i in dept_data:
        labels.append(i['dept_name'])
        registrations.append(i['total_reg'])
        paid_reg.append(i['paid_reg'])
        revenue.append(i['total_revenue'] or 0)

    return render(request,'super_admin.html',{
        'total_reg':total_reg,
        'total_event':total_event,
        'paid_revenue':paid_revenue,
        'unpaid_revenue':unpaid_revenue,
        'percent':percent,
        'approve_event':approve_event,
        'pending_event':pending_event,

        'labels':labels,
        'registrations':registrations,
        'paid_reg':paid_reg,
        'revenue':revenue
    })
def AddCollege(request):
    return render(request,'add_college.html')
def ViewCollege(request):
    college = DepartmentDb.objects.all()
    return render(request,'view_college.html',{'college':college})
def Save_college(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        email = request.POST.get('email')
        mobile = request.POST.get('mob')
        hod = request.POST.get('hod')
        cuname = request.POST.get('college_uname')
        cpswd = request.POST.get('college_pswd')
        obj = DepartmentDb(name=name,code=code,email=email,mob=mobile,hod=hod,cuname=cuname,cpswd=cpswd)
        obj.save()
        messages.success(request,"Department Added Successfully")
        return redirect(ViewCollege)
def delete_college(request,college_id):
    college = DepartmentDb.objects.filter(id=college_id)
    college.delete()
    messages.success(request,"Department Deleted Successfully")
    return redirect(ViewCollege)
def EditCollege(request,college_id):
    college = DepartmentDb.objects.get(id=college_id)
    return render(request,'edit_college.html',{'college':college})
def update_college(request,college_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        email = request.POST.get('email')
        mobile = request.POST.get('mob')
        hod = request.POST.get('hod')
        cuname = request.POST.get('college_uname')
        cpswd = request.POST.get('college_pswd')
        DepartmentDb.objects.filter(id=college_id).update(name=name,code=code,email=email,mob=mobile,hod=hod,cuname=cuname,cpswd=cpswd)
        messages.success(request,"Department Updated Successfully")
        return redirect(ViewCollege)

def login_page(request):
    return render(request,'login_page.html')

def admin_login(request):
    if request.method == "POST":
        uname = request.POST.get('username')
        pswd = request.POST.get('password')
    #college admin if
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
    #department admin if
    elif DepartmentDb.objects.filter(cuname=uname, cpswd=pswd).exists():
        dept = DepartmentDb.objects.filter(cuname=uname,cpswd=pswd).first()
        request.session['username'] = uname
        request.session['password'] = pswd
        request.session['department'] = dept.code
        return redirect(CollegeAdminPanel)
    else:
        print("User not found..!")
        return redirect(login_page)

def admin_logout(request):
    del request.session['username']
    del request.session['password']
    return redirect(login_page)

def CollegeAdminPanel(request):
    #Department Cards
    uname = request.session.get('username')
    dept = DepartmentDb.objects.get(cuname=uname)
    total_reg = RegistrationDb.objects.filter(dept_name=dept.code).count()
    paid_data = RegistrationDb.objects.filter(dept_name=dept.code,pay_status='Paid').aggregate(total=Sum('fee'))
    revenue = paid_data['total'] or 0
    pending_data = RegistrationDb.objects.filter(dept_name=dept.code,pay_status='Unpaid').aggregate(total=Sum('fee'))
    unpaid_revenue = pending_data['total'] or 0
    total_events = EventDb.objects.filter(euname=dept.code).count()
    approve_event = EventDb.objects.filter(euname=dept.code,status='Approved').count()
    pending_event = EventDb.objects.filter(euname=dept.code, status='Pending').count()
    attended = RegistrationDb.objects.filter(dept_name=dept.code,sattendance='Present').count()
    attendance_percent = round((attended / total_reg * 100), 2) if total_reg else 0

    #Event Chart
    latest_events = EventDb.objects.filter(euname=dept.code).order_by('-id').values_list('title', flat=True)[:5]
    event_data = RegistrationDb.objects.filter(dept_name=dept.code, event_name__in=latest_events).values('event_name').annotate(
        total_reg=Count('id'),
        paid_reg=Count('id', filter=Q(pay_status='Paid')),
        attended_reg=Count('id', filter=Q(sattendance='Present'))
    )
    event_data_dic = {i['event_name']: i for i in event_data}
    labels = []
    total_reg_data = []
    paid_reg_data = []
    attended_data =[]
    for event in latest_events:
        i = event_data_dic.get(event, {})
        labels.append(event)
        total_reg_data.append(i.get('total_reg', 0))
        paid_reg_data.append(i.get('paid_reg', 0))
        attended_data.append(i.get('attended_reg', 0))

    #Event Leaderboard
    top_events = RegistrationDb.objects.filter(dept_name=dept.code).values('event_name').annotate(
        paid_reg=Count('id', filter=Q(pay_status='Paid'))
    ).order_by('-paid_reg')[:10]
    leaderboard = []
    for i,j in enumerate(top_events, start=1):
        leaderboard.append({
            "rank": i,
            "event": j['event_name'],
            "count": j['paid_reg']
        })

    return render(request,'college_admin.html',{
        'total_reg':total_reg,
        'revenue':revenue,
        'unpaid_revenue':unpaid_revenue,
        'total_events':total_events,
        'approve_event':approve_event,
        'pending_event':pending_event,
        'attendance_percent':attendance_percent,

        'event_labels':labels,
        'event_total':total_reg_data,
        'event_paid':paid_reg_data,
        'event_attended':attended_data,

        'leaderboard':leaderboard
    })

def AddEvent(request):
    return render(request,'add_event.html')
def Save_event(request):
    if request.method == "POST":
        euname = request.POST.get('euname')
        title = request.POST.get('title')
        desc = request.POST.get('description')
        type = request.POST.get('type')
        start = request.POST.get('start')
        end = request.POST.get('end')
        dead = request.POST.get('dead')
        mode = request.POST.get('mode')
        loc = request.POST.get('location')
        maxS = request.POST.get('maxS')
        fee = request.POST.get('fee')
        certify = request.FILES['certificate']
        poster = request.FILES['poster']
        obj = EventDb(euname=euname,title=title,description=desc,type=type,start=start,end=end,dead=dead,mode=mode,location=loc,maxS=maxS,fee=fee,certificate=certify,poster=poster)
        obj.save()
        return redirect(AddEvent)
def view_event(request):
    uname = request.session.get('department')
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
        messages.success(request,"Event Approved Successfully")
        return redirect(all_event)
def delete_event(request,delete_id):
    event = EventDb.objects.filter(id=delete_id)
    event.delete()
    return redirect(view_event)

def college_registered_events(request):
    uname = request.session.get('department')
    event = EventDb.objects.filter(euname=uname)
    return render(request,'view_registrations.html',{'event':event})

def student_registrations(request,viewreg_id):
    eventname = EventDb.objects.get(id=viewreg_id)
    registered = RegistrationDb.objects.filter(event_name=eventname.title)
    return render(request,'student_registrations.html',{'registered':registered})

def delete_register(request,delete_id):
    registered = RegistrationDb.objects.filter(id=delete_id)
    registered.delete()
    return redirect(college_registered_events)


def certificate_editor(request,e_certi):
    event = EventDb.objects.get(id=e_certi)
    return render(request,"certificate_editor.html",{"event":event})
def save_positions(request):
    data = json.loads(request.body)
    event = EventDb.objects.get(id=data["event_id"])

    event.name_x = data["name_x"]
    event.name_y = data["name_y"]

    event.event_x = data["event_x"]
    event.event_y = data["event_y"]

    event.date_x = data["date_x"]
    event.date_y = data["date_y"]

    event.qr_x = data["qr_x"]
    event.qr_y = data["qr_y"]

    event.save()
    return HttpResponse(status=204)



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

        #certificate generation
        event = EventDb.objects.filter(title=s_event).first()
        img = Image.open(event.certificate.path)
        img_width, img_height = img.size
        dispaly_width = 500
        scale = img_width / dispaly_width

        name_x = int(event.name_x * scale)
        name_y = int(event.name_y * scale)
        event_x = int(event.event_x * scale)
        event_y = int(event.event_y * scale)
        date_x = int(event.date_x * scale)
        date_y = int(event.date_y * scale)
        qr_x = int(event.qr_x * scale)
        qr_y = int(event.qr_y * scale)


        base_font_size = 20
        font_size = int(base_font_size * scale)
        font = ImageFont.truetype("arial.ttf", font_size)

        reg = RegistrationDb.objects.get(sname = s_name,event_name = s_event)
        qr_img = Image.open(reg.qr_image.path).convert("RGB")
        base_qr_size = 80
        qr_size = int(base_qr_size * scale)
        qr_img = qr_img.resize((qr_size,qr_size), Image.NEAREST)
        img.paste(qr_img,(qr_x,qr_y))

        draw = ImageDraw.Draw(img)

        # text_bbox = draw.textbbox((0,0), event.title, font=font)
        # text_width = text_bbox[2] - text_bbox[0]
        # center_x_event = (img_width - text_width) // 2


        draw.text((name_x, name_y), s_name, fill="black", font=font)
        draw.text((event_x, event_y), event.title, fill="black", font=font)
        draw.text((date_x, date_y), str(event.start), fill="black", font=font)


        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"{s_name}_{s_event}.png"
        reg.certificate_image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )



        email = EmailMessage(
            subject=event.title,
            body="Thank you for participating our program, your certificate is attached with this email.For any issues, contact to our website.",
            from_email="cirileb2003@gmail.com",
            to=[s_email]
        )
        email.attach(
            filename,
            buffer.getvalue(),
            "image/png"
        )
        email.send()

        return HttpResponse(status=204)



