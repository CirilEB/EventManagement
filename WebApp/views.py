from django.shortcuts import render, redirect
import json
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from SuperAdmin.models import EventDb
from WebApp.models import RegistrationDb


# Create your views here.
def Home(request):
    return render(request,'Home.html')
def About(request):
    return render(request,'About.html')
def Contact(request):
    return render(request,'Contact.html')
def Events(request):
    Allevents = EventDb.objects.all()
    return render(request,'Events.html',{'Allevents':Allevents})
def Register(request,event_id):
    register = EventDb.objects.get(id=event_id)
    return render(request,'Register.html',{'register':register})
def Save_registration(request):
    if request.method == "POST":
        event_name = request.POST.get('event_name')
        sname = request.POST.get('sname')
        semail = request.POST.get('semail')
        scollege = request.POST.get('scollege')
        sdept = request.POST.get('sdept')
        syear = request.POST.get('syear')
        smob = request.POST.get('smob')
        obj = RegistrationDb(event_name=event_name,sname=sname,semail=semail,scollege=scollege,sdept=sdept,syear=syear,smob=smob)
        obj.save()

        # qrcode generation
        data = {
            "name" : sname,
            "college" : scollege,
            "department" : sdept,
            "year" : syear,
            "email" : semail,
            "mobile" : smob
        }
        json_data = json.dumps(data)
        qr = qrcode.make(json_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        # email  notification
        email_message = EmailMessage(
            subject = event_name,
            body="Thank you for your registration.Use the QRcode below for Attendance and Certificate collection",
            from_email="cirileb2003@gmail.com",
            to = [semail]
        )
        email_message.attach("Event_QR.png",buffer.getvalue(),"images/png")
        email_message.send()
        return redirect(Events)


