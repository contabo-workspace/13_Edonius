#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_conf.settings.dev')
django.setup()

from django.template.loader import get_template

print("Testing templates...\n")

for tmpl in ['navbar.html', 'sidebar.html']:
    try:
        t = get_template(tmpl)
        print(f"✓ {tmpl} OK")
    except Exception as e:
        print(f"✗ {tmpl} ERROR:\n  {str(e)[:300]}\n")
