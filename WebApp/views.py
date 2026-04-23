from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.db.models import Avg
import json
import qrcode
import random
import requests
import razorpay
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from SuperAdmin.models import EventDb, DepartmentDb
from WebApp.models import RegistrationDb, StudentDb
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password


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
def Events(request):
    alldepartments = DepartmentDb.objects.all()
    Completed = EventDb.objects.filter(is_archived=True)
    Current = EventDb.objects.filter(is_archived=False)
    return render(request,'Events.html',{
        'Completed':Completed,
        'Current':Current,
        'alldepartments':alldepartments
    })
def Register(request,event_id):
    alldepartments = DepartmentDb.objects.all()
    register = EventDb.objects.get(id=event_id)
    today = timezone.now().date()
    total_reg = RegistrationDb.objects.filter(event_name=register.title).count()
    reviews = RegistrationDb.objects.filter(event_name=register.title,rating__isnull=False).order_by('-commented_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    return render(request,'Register.html',{
        'register':register,
        'alldepartments':alldepartments,
        'today':today,
        'total_reg':total_reg,
        'reviews':reviews,
        'avg_rating':round(avg_rating,1)
    })
def Payment(request,stud_id):
    alldepartments = DepartmentDb.objects.all()
    student = RegistrationDb.objects.get(id=stud_id)
    test_key = settings.RAZORPAY_KEY_TEST
    pay = student.fee
    amount = int(pay*100)
    pay_str = str(amount)
    if request.method == "POST":
            order_currency = "INR"
            client = razorpay.Client(auth=(test_key,settings.RAZORPAY_KEY_SECRET))
            payment = client.order.create({'amount':amount,'currency':order_currency})
            student.razorpay_order_id = payment["id"]
            student.save()
            return render(request,'Payment_page.html',{
                'alldepartments': alldepartments,
                'test_key':test_key,
                'pay_str':pay_str,
                'payment':payment,
                'student':student,
                'stud_id':stud_id
            })
    return render(request, 'Payment_page.html', {
        'alldepartments': alldepartments,
        'test_key':test_key,
        'pay_str': pay_str,
        'student': student,
        'stud_id':stud_id
    })
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")
        test_key = settings.RAZORPAY_KEY_TEST
        client = razorpay.Client(auth=(test_key,settings.RAZORPAY_KEY_SECRET))
        params = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            client.utility.verify_payment_signature(params)
            student = RegistrationDb.objects.get(razorpay_order_id=order_id)
            event = EventDb.objects.get(title=student.event_name)
            student.pay_status = "Paid"
            student.save()
            # email notification

            email_message = EmailMessage(
                subject=student.event_name,
                body="",
                from_email=settings.EMAIL_HOST_USER,
                to=[student.semail]
            )
            email_message.content_subtype = "html"
            email_message.body = f"""
                                    <h4><strong>{student.event_name}</strong></h4>
                                    <p>This email is from ESEC event portal</p>
                                    
                                    <p><strong>Student Details</strong></p>
                                    <hr>
                                    <p><b>Name:</b>{student.sname}</p>
                                    <p><b>Amount:</b>{student.fee}</p>
                                    <p><b>Order id:</b>{student.razorpay_order_id}</p>
                                    
                                    <p><strong>{event.title} - {event.type} Details</strong></p>
                                    <hr>
                                    <p><b>Starting :</b>{event.start}</p>
                                    <p><b>Ending :</b>{event.end}</p>
                                    <p><b>Event Mode:</b>{event.mode}</p>
                                    <p><b>Venue:</b>{event.location}</p>
                                    
                                    <p><b>Message:<br>Your payment for {student.event_name} was successful.Thank you for registering and paying forward.Make use of below QR code to mark your attendance and to generate participation certificate</b></p>
                                    <p style="color:red;">Note:If this email got deleted,you can still download your QR code from our site</p>
                                    """
            file_url = student.qr_image.url
            response = requests.get(file_url)
            email_message.attach(
                student.qr_image.name.split('/')[-1],
                response.content,
                'image/png'
            )
            email_message.send()
            return JsonResponse({
                "status":"success",
                "message":"Payment verified"
            })
        except:
            return JsonResponse({
                "status": "failed",
                "message": "Payment not verified"
            })

def Save_registration(request):
    if request.method == "POST":
        Logname = request.session.get('Logname')
        dept_name = request.POST.get('dept_name')
        event_name = request.POST.get('event_name')
        event_date = request.POST.get('event_date')
        fee = request.POST.get('fee')
        sname = request.POST.get('sname')
        semail = request.POST.get('semail')
        scollege = request.POST.get('scollege')
        sdept = request.POST.get('sdept')
        syear = request.POST.get('syear')
        smob = request.POST.get('smob')
        obj = RegistrationDb(Logname=Logname,dept_name=dept_name,event_name=event_name,event_date=event_date,fee=fee,sname=sname,semail=semail,scollege=scollege,sdept=sdept,syear=syear,smob=smob)

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
        messages.success(request,"Registered Successfully - Pay Now or Later")
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
    reg_filter_by_log = RegistrationDb.objects.filter(Logname=student)
    eventArchived = EventDb.objects.filter(is_archived=True).values_list("title","euname")
    registrations = []
    for i in reg_filter_by_log:
        is_archived = (i.event_name,i.dept_name) in eventArchived
        if not is_archived or i.sattendance == "Present":
            registrations.append(i)
    reg_present = RegistrationDb.objects.filter(Logname=student,sattendance="Present").count()
    reg_absent = RegistrationDb.objects.filter(Logname=student,sattendance="Absent").count()
    total_reg = RegistrationDb.objects.filter(Logname=student).count()
    obj = RegistrationDb.objects.last()
    return render(request,'MyRegistrations.html',{
        'student':student,
        'registrations':registrations,
        'reg_present':reg_present,
        'reg_absent':reg_absent,
        'total_reg':total_reg,
        'alldepartments':alldepartments
    })
def student_loginPage(request):
    student = request.session.get('student_name')
    if student:
        student_data = StudentDb.objects.get(student_name=student)
        if student_data.is_verified == False:
            student_data.delete()
        del request.session['student_name']
    return render(request,'student_login.html')
def student_signup(request):
    return render(request,'student_signup.html')
def check_username(request):
    username = request.GET.get('username')
    exists = StudentDb.objects.filter(student_name=username).exists()
    return JsonResponse({'exists':exists})
def save_signup(request):
    if request.method == "POST":
        student_name = request.POST.get('student_name')
        student_email = request.POST.get('student_email')
        student_pass_original = request.POST.get('student_pass')
        student_pass = make_password(student_pass_original)
        otp = random.randint(100000,999999)
        obj = StudentDb(student_name=student_name,student_email=student_email,student_pass=student_pass,student_otp=otp)
        obj.save()
        request.session['student_name'] = student_name
        email_message = EmailMessage(
            subject="OTP Verification",
            body="",
            from_email="cirileb2003@gmail.com",
            to=[student_email]
        )
        email_message.content_subtype = "html"
        email_message.body = f"""
                        <p><strong>Ready to Register?</strong></p>
                        <p>This email is from ESEC event portal</p>

                        <p><b>Message:<br>Your OTP to register for ESEC event portal {str(otp)}</b></p>
                        <p style="color:red;">Note:This otp will be expired after five minutes</p>
                        """
        email_message.send()

        return redirect(verify_otp)
def verify_otp(request):
    return render(request,'otp_verificationPage.html')
def verify_otp_forgot(request):
    return render(request, 'otp_verifyForgot.html')
def check_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('enterotp')
        student_name = request.session.get('student_name')
        student = StudentDb.objects.get(student_name=student_name)
        if timezone.now() > student.created_at + timedelta(minutes=5):
            student.delete()
            del request.session['student_name']
            messages.error(request, "OTP Expired !")
            return redirect(student_signup)
        if student.student_otp == entered_otp:
            student.is_verified = True
            student.save()
            del request.session['student_name']
            messages.success(request,"OTP Verified and Registered Successfully")
            return redirect(student_loginPage)
        else:
            messages.error(request,"Incorrect OTP !")
            return redirect(verify_otp)
def login_check(request):
    if request.method == "POST":
        Lname = request.POST.get('name')
        Lpass = request.POST.get('pass')
        LogStudent = StudentDb.objects.filter(student_name=Lname).first()
        if LogStudent and check_password(Lpass,LogStudent.student_pass):
            request.session['Logname'] = Lname
            messages.success(request,"Successfully Logged in")
            return redirect(Home)
        else:
            messages.error(request, "Unknown Credentials - Try Again !")
            return redirect(student_loginPage)
def signout(request):
    del request.session['Logname']
    messages.success(request,"Logged out Successfully")
    return redirect(Home)
def submit_review(request,regId):
    reg = RegistrationDb.objects.get(id=regId)
    if request.method == "POST":
        reg.rating = request.POST.get('rating')
        reg.comment = request.POST.get('comment')
        reg.commented_at = timezone.now()
        reg.save()
        messages.success(request,"Comment Added! Thank you for your Contribution")
        return redirect(MyRegistrations)

def ForgotPassword(request):
    return render(request,'Forgot_Password.html')
def submit_forgot(request):
    if request.method == "POST":
        uname = request.POST.get('name')
        pass_original = request.POST.get('pass')
        pswd = make_password(pass_original)
        otp = random.randint(100000, 999999)
        if not StudentDb.objects.filter(student_name=uname).exists():
            messages.error(request,"Username does not exists !")
            return redirect(ForgotPassword)
        else:
            LogStudent = StudentDb.objects.filter(student_name=uname).first()
            StudentDb.objects.filter(student_name=uname).update(student_otp=otp,created_at=timezone.now())
            request.session['student_name'] = uname
            request.session['student_pass'] = pswd
            email_message = EmailMessage(
                subject="OTP Verification",
                body="",
                from_email="cirileb2003@gmail.com",
                to=[LogStudent.student_email]
            )
            email_message.content_subtype = "html"
            email_message.body = f"""
                    <p><strong>Forgot Your Password?</strong></p>
                    <p>This email is from ESEC event portal</p>
    
                    <p><b>Message:<br>Your OTP to change your old password {str(otp)}</b></p>
                    <p style="color:red;">Note:This otp will be expired after two minutes</p>
                    """
            email_message.send()
            return redirect(verify_otp_forgot)
def check_otp_pass(request):
    if request.method == "POST":
        entered_otp = request.POST.get('enterotp')
        student_name = request.session.get('student_name')
        student_pass = request.session.get('student_pass')
        student = StudentDb.objects.get(student_name=student_name)
        if timezone.now() > student.created_at + timedelta(minutes=2):
            del request.session['student_name']
            del request.session['student_pass']
            messages.error(request, "OTP Expired !")
            return redirect(ForgotPassword)
        if student.student_otp == entered_otp:
            student.student_pass = student_pass
            student.save()
            del request.session['student_name']
            del request.session['student_pass']
            messages.success(request,"OTP Verified and Password Changed!")
            return redirect(student_loginPage)
        else:
            messages.error(request,"Incorrect OTP !")
            return redirect(verify_otp_forgot)


def Contact_Message(request):
    if request.method == "POST":
        name = request.POST.get('contact_name')
        email = request.POST.get('contact_email')
        subject = request.POST.get('contact_subject')
        message = request.POST.get('contact_message')
        email_message = EmailMessage(
            subject=subject,
            body="",
            from_email=email,
            to=["cirileb2003@gmail.com"]
        )
        email_message.content_subtype = "html"
        email_message.body = f"""
        <p><strong>New Contact Message From Event Management</strong></p>
        
        <p><b>Name:</b>{name}</p>
        <p><b>Email:</b>{email}</p>
        
        <p><b>Message:</b><br>{message}</p>
        """
        email_message.send()
        messages.success(request,"Message Send Successfully!")
        return redirect(Home)


def mock_success(request,reg_id):
    student = RegistrationDb.objects.get(id=reg_id)
    event = EventDb.objects.get(title=student.event_name)
    student.razorpay_order_id = "mock success"
    student.pay_status = "Paid"
    student.save()
    # email notification

    email_message = EmailMessage(
        subject=student.event_name,
        body="",
        from_email=settings.EMAIL_HOST_USER,
        to=[student.semail]
    )
    email_message.content_subtype = "html"
    email_message.body = f"""
                                        <h4><strong>{student.event_name}</strong></h4>
                                        <p>This email is from ESEC event portal</p>

                                        <p><strong>Student Details</strong></p>
                                        <hr>
                                        <p><b>Name:</b>{student.sname}</p>
                                        <p><b>Amount:</b>{student.fee}</p>
                                        <p><b>Order id:</b>{student.razorpay_order_id}</p>

                                        <p><strong>{event.title} - {event.type} Details</strong></p>
                                        <hr>
                                        <p><b>Starting :</b>{event.start}</p>
                                        <p><b>Ending :</b>{event.end}</p>
                                        <p><b>Event Mode:</b>{event.mode}</p>
                                        <p><b>Venue:</b>{event.location}</p>

                                        <p><b>Message:<br>Your payment for {student.event_name} was successful.Thank you for registering and paying forward.Make use of below QR code to mark your attendance and to generate participation certificate</b></p>
                                        <p style="color:red;">Note:If this email got deleted,you can still download your QR code from our site</p>
                                        """
    file_url = student.qr_image.url
    response = requests.get(file_url)
    email_message.attach(
        student.qr_image.name.split('/')[-1],
        response.content,
        'image/png'
    )
    email_message.send()
    messages.success(request,"Payment Successful!")
    return redirect(MyRegistrations)
def mock_failed(request,reg_id):
    student = RegistrationDb.objects.get(id=reg_id)
    student.razorpay_order_id = "mock failed"
    student.save()
    messages.error(request,"Payment Failed!")
    return redirect(MyRegistrations)

