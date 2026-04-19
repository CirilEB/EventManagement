import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','EventManagement.settings')
django.setup()
from django.contrib.auth.models import User
username = "ESEC"
email = "cirileb44@gmail.com"
password = "Esec@123"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username,email,password)
    print("Superuser created")
else:
    print("Superuser already exists")