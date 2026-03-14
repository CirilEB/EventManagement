from django.urls import path
from WebApp import views

urlpatterns=[
    path('Home/',views.Home,name='Home'),
    path('About/',views.About,name='About'),
    path('Contact/',views.Contact,name='Contact'),
    path('Events/',views.Events,name='Events'),
    path('Register/<int:event_id>/',views.Register,name='Register'),
    path('Save_registration',views.Save_registration,name='Save_registration'),
    path('qr_valid/',views.qr_valid,name='qr_valid'),
    path('process_qr/',views.process_qr,name='process_qr'),
    path('MyRegistrations/',views.MyRegistrations,name='MyRegistrations'),
    path('student_loginPage/',views.student_loginPage,name='student_loginPage'),
    path('student_signup/',views.student_signup,name='student_signup'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('save_signup',views.save_signup,name='save_signup'),
    path('check_otp',views.check_otp,name='check_otp'),
    path('login_check',views.login_check,name='login_check'),
    path('filteredEvents/<dept_name>/',views.filteredEvents,name='filteredEvents'),
    path('signout',views.signout,name='signout')
]