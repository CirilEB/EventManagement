from django.urls import path
from SuperAdmin import views
from SuperAdmin.views import login_page

urlpatterns=[
    path('Dashboard-College/',views.SuperAdminPanel,name='SuperAdmin'),
    path('AddCollege/',views.AddCollege,name='AddCollege'),
    path('ViewCollege/', views.ViewCollege,name='ViewCollege'),
    path('Save_college',views.Save_college,name='Save_college'),
    path('delete_college/<int:college_id>', views.delete_college,name='delete_college'),
    path('edit_college/<int:college_id>/', views.EditCollege, name='edit_college'),
    path('update_college/<int:college_id>', views.update_college,name='update_college'),
    path('login_page/',views.login_page,name='login_page'),
    path('admin_login',views.admin_login,name='admin_login'),
    path('admin_logout',views.admin_logout,name='admin_logout'),
    path('Dashboard-Department/',views.CollegeAdminPanel,name='CollegeAdminPanel'),
    path('AddEvent/', views.AddEvent, name='AddEvent'),
    path('Save_event',views.Save_event,name='Save_event'),
    path('ViewEvent/',views.view_event,name='view_event'),
    path('all_event/',views.all_event,name='all_event'),
    path('event_approval/<int:approval_id>',views.event_approval,name='event_approval'),
    path('delete_event/<int:delete_id>', views.delete_event, name='delete_event'),
    path('Registrations/',views.college_registered_events,name='registrations'),
    path('student_registrations/<int:viewreg_id>/',views.student_registrations,name='student_registrations'),
    path('delete_register/<int:delete_id>', views.delete_register, name='delete_register'),
    path('QrScanPage/',views.QrScanPage,name='QrScanPage'),
    path('process-qr/',views.process_qr,name='process_qr'),
    path('certificate_editor/<int:e_certi>/',views.certificate_editor,name='certificate_editor'),
    path('save-positions/',views.save_positions,name='save_positions'),
    path('check_username/',views.check_username,name='check_username'),
    path('presentOffline/<int:stud_id>/',views.presentOffline,name='presentOffline')
]