#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muni_account.settings')
django.setup()

try:
    from accounts.forms import RootCreateUserForm
    print('✓ Form imported successfully')
    
    form = RootCreateUserForm()
    print('✓ Form instantiated successfully')
    print('✓ Form fields:', list(form.fields.keys()))
    
    # Test rendering
    html = str(form['username'])
    print('✓ Form field rendering works')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
