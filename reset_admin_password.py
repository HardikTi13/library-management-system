import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_checkout.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
new_password = "admin123"

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✅ Admin user updated successfully!")
    print(f"   Username: {username}")
    print(f"   Password: {new_password}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Superuser: {user.is_superuser}")
except User.DoesNotExist:
    print(f"❌ User '{username}' does not exist.")
