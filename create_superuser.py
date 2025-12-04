import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_checkout.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@example.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superuser '{username}' created successfully!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
else:
    print(f"ℹ️  Superuser '{username}' already exists.")
