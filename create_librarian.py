"""
Script to create a librarian user for testing role-based routing.
Run this script to create a librarian account.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_checkout.settings')
django.setup()

from django.contrib.auth.models import User
from circulation.models import UserProfile

def create_librarian():
    # Create or get librarian user
    username = 'librarian'
    password = 'librarian123'
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': 'librarian@library.com'}
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created user: {username}")
    else:
        print(f"✓ User already exists: {username}")
    
    # Create or update UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'user_type': 'LIBRARIAN'}
    )
    
    if created:
        print(f"✓ Created librarian profile for: {username}")
    else:
        # Update to librarian if it exists but is not a librarian
        if profile.user_type != 'LIBRARIAN':
            profile.user_type = 'LIBRARIAN'
            profile.save()
            print(f"✓ Updated profile to LIBRARIAN for: {username}")
        else:
            print(f"✓ Librarian profile already exists for: {username}")
    
    print(f"\n✅ Librarian account ready!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Type: LIBRARIAN")

if __name__ == '__main__':
    create_librarian()
