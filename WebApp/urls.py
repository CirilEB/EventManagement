from django.urls import path
from WebApp import views

urlpatterns=[
    path('Home/',views.Home,name='Home'),
    path('About/',views.About,name='About'),
    path('Contact/',views.Contact,name='Contact'),
    path('Events/',views.Events,name='Events'),
    path('Register/<int:event_id>/',views.Register,name='Register'),
    path('Save_registration',views.Save_registration,name='Save_registration')
]