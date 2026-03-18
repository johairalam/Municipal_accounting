#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muni_account.settings')
django.setup()

from accounts.models import User
from accounts.views import role_required
from django.test import RequestFactory
from django.http import HttpResponse

# Create a test user with DEV role
test_user, created = User.objects.get_or_create(
    username='testdev',
    defaults={'email': 'testdev@test.com', 'role': 'DEV'}
)
print(f'Test user: {test_user.username}, Role: {test_user.role}')

# Test the decorator
@role_required(['DEV'])
def test_view(request):
    return HttpResponse('Success')

# Create fake request
factory = RequestFactory()
request = factory.get('/test/')
request.user = test_user

try:
    response = test_view(request)
    print(f'✓ Decorator test passed: {response.status_code}')
except Exception as e:
    print(f'✗ Decorator error: {e}')
