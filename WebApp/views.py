from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json
import qrcode
import random
import razorpay
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from SuperAdmin.models import EventDb, DepartmentDb
from WebApp.models import RegistrationDb, StudentDb


# Create your views here.
def Home(request):
    student = request.session.get('Logname')
    alldepartments = DepartmentDb.objects.all()
    return render(request,'Home.html',{
        'student':student,
        'alldepartments':alldepartments
    })
def filteredEvents(request,dept_name):
    filtered = EventDb.objects.filter(euname=dept_name)
    filter_name = DepartmentDb.objects.get(code=dept_name)
    alldepartments = DepartmentDb.objects.all()
    return render(request,'filtered_events.html',{
        'filtered':filtered,
        'filter_name':filter_name,
        'alldepartments':alldepartments
    })
def About(request):
    alldepartments = DepartmentDb.objects.all()
    return render(request,'About.html',{'alldepartments':alldepartments})
def Contact(request):
    alldepartments = DepartmentDb.objects.all()
    return render(request,'Contact.html',{'alldepartments':alldepartments})
def Events(request):
    alldepartments = DepartmentDb.objects.all()
    Allevents = EventDb.objects.all()
    return render(request,'Events.html',{
        'Allevents':Allevents,
        'alldepartments':alldepartments
    })
def Register(request,event_id):
    alldepartments = DepartmentDb.objects.all()
    register = EventDb.objects.get(id=event_id)
    return render(request,'Register.html',{
        'register':register,
        'alldepartments':alldepartments
    })
def Payment(request,stud_id):
    alldepartments = DepartmentDb.objects.all()
    student = RegistrationDb.objects.get(id=stud_id)
    pay = student.fee
    amount = int(pay*100)
    pay_str = str(amount)
    if request.method == "POST":
            order_currency = "INR"
            client = razorpay.Client(auth=('rzp_test_SRUNBwpvVW3waU',settings.RAZORPAY_KEY_SECRET))
            payment = client.order.create({'amount':amount,'currency':order_currency})
            student.razorpay_order_id = payment["id"]
            student.save()
            return render(request,'Payment_page.html',{
                'alldepartments': alldepartments,
                'pay_str':pay_str,
                'payment':payment,
                'student':student
            })
    return render(request, 'Payment_page.html', {
        'alldepartments': alldepartments,
        'pay_str': pay_str,
        'student': student
    })
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")
        client = razorpay.Client(auth=('rzp_test_SRUNBwpvVW3waU',settings.RAZORPAY_KEY_SECRET))
        params = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            client.utility.verify_payment_signature(params)
            student = RegistrationDb.objects.get(razorpay_order_id=order_id)
            student.pay_status = "Paid"
            student.save()
            # email notification

            email_message = EmailMessage(
                subject=student.event_name,
                body="Thank you for your registration.Use the QRcode below for Attendance and Certificate collection",
                from_email=settings.EMAIL_HOST_USER,
                to=[student.semail]
            )
            email_message.attach_file(student.qr_image.path)
            email_message.send()
            return redirect(MyRegistrations)
        except:
            return HttpResponse(404)

def Save_registration(request):
    if request.method == "POST":
        Logname = request.session.get('Logname')
        event_name = request.POST.get('event_name')
        event_date = request.POST.get('event_date')
        fee = request.POST.get('fee')
        sname = request.POST.get('sname')
        semail = request.POST.get('semail')
        scollege = request.POST.get('scollege')
        sdept = request.POST.get('sdept')
        syear = request.POST.get('syear')
        smob = request.POST.get('smob')
        obj = RegistrationDb(Logname=Logname,event_name=event_name,event_date=event_date,fee=fee,sname=sname,semail=semail,scollege=scollege,sdept=sdept,syear=syear,smob=smob)

        # qrcode generation
        data = {
            "name" : sname,
            "college" : scollege,
            "department" : sdept,
            "year" : syear,
            "email" : semail,
            "mobile" : smob,
            "event" : event_name,
            "status" : "NotVerified",
            "message": "NotVerified"
        }
        json_data = json.dumps(data)
        qr = qrcode.make(json_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        # save image to media
        filename = f"{sname}_{event_name}_qr.png"
        obj.qr_image.save(filename, ContentFile(buffer.getvalue()), save=True)

        obj.save()

        return redirect(MyRegistrations)


def qr_valid(request):
    alldepartments = DepartmentDb.objects.all()
    return render(request,'qr_verify.html',{'alldepartments':alldepartments})
@csrf_exempt
def process_qr(request):
    if request.method == "POST":
        data = json.loads(request.body)
        s_name = data.get("name")
        s_email = data.get("email")
        s_mob = data.get("mobile")
        s_event = data.get("event")
        print(s_name,s_email,s_mob,s_event)
        reg = RegistrationDb.objects.filter(
            sname = s_name,
            event_name = s_event,
        ).first()
        if reg is None:
            return JsonResponse({"status":"error","message":"Unknown Credentials"})
        elif reg.sattendance == "Present":
            return JsonResponse({"status":"success","message":"Verified Certificate"})
        else:
            return JsonResponse({"status":"error","message":"Unknown Credentials"})

        return HttpResponse(status=204)

def MyRegistrations(request):
    alldepartments = DepartmentDb.objects.all()
    student = request.session.get('Logname')
    registrations = RegistrationDb.objects.filter(Logname=student)
    reg_present = RegistrationDb.objects.filter(Logname=student,sattendance="Present").count()
    reg_absent = RegistrationDb.objects.filter(Logname=student,sattendance="Absent").count()
    total_reg = RegistrationDb.objects.filter(Logname=student).count()
    return render(request,'MyRegistrations.html',{
        'student':student,
        'registrations':registrations,
        'reg_present':reg_present,
        'reg_absent':reg_absent,
        'total_reg':total_reg,
        'alldepartments':alldepartments
    })
def student_loginPage(request):
    return render(request,'student_login.html')
def student_signup(request):
    return render(request,'student_signup.html')
def save_signup(request):
    if request.method == "POST":
        student_name = request.POST.get('student_name')
        student_email = request.POST.get('student_email')
        student_pass = request.POST.get('student_pass')
        otp = random.randint(100000,999999)
        obj = StudentDb(student_name=student_name,student_email=student_email,student_pass=student_pass,student_otp=otp)
        obj.save()
        request.session['student_name'] = student_name
        email_message = EmailMessage(
            subject="OTP Verification",
            body="Your OTP to register for Event Registraion Portal is " + str(otp),
            from_email="cirileb2003@gmail.com",
            to=[student_email]
        )
        email_message.send()

        return redirect(verify_otp)
def verify_otp(request):
    return render(request,'otp_verificationPage.html')
def check_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('enterotp')
        student_name = request.session.get('student_name')
        student = StudentDb.objects.get(student_name=student_name)
        del request.session['student_name']
        if timezone.now() > student.created_at + timedelta(minutes=5):
            student.delete()
            return redirect(student_signup)
        if student.student_otp == entered_otp:
            student.is_verified = True
            student.save()
            return redirect(student_loginPage)
def login_check(request):
    if request.method == "POST":
        Lname = request.POST.get('name')
        Lpass = request.POST.get('pass')
        if StudentDb.objects.filter(student_name=Lname,student_pass=Lpass).exists():
            request.session['Logname'] = Lname
            return redirect(Home)
        else:
            return redirect(student_loginPage)
def signout(request):
    del request.session['Logname']
    return redirect(Home)
