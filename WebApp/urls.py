from django.urls import path
from WebApp import views

urlpatterns=[
    path('Home/',views.Home,name='Home'),
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
    path('signout',views.signout,name='signout'),
    path('Payment/<int:stud_id>/',views.Payment,name='Payment'),
    path('verify_payment',views.verify_payment,name='verify_payment'),
    path('check_username/',views.check_username,name='check_username'),
    path('review/<int:regId>/',views.submit_review,name='submit_review'),
    path('ForgotPassword/',views.ForgotPassword,name='ForgotPassword'),
    path('submit_forgot',views.submit_forgot,name='submit_forgot'),
    path('check_otp_pass',views.check_otp_pass,name='check_otp_pass'),
    path('verify_otp_forgot/',views.verify_otp_forgot,name='verify_otp_forgot'),
    path('Contact_Message',views.Contact_Message,name='Contact_Message'),
    path('mock_success/<int:reg_id>',views.mock_success,name='mock_success'),
    path('mock_failed/<int:reg_id>',views.mock_failed,name='mock_failed')
]