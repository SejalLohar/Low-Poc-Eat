import json
from django.core.management import call_command
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')

import django
django.setup()

output_file = 'data.json'

with open(output_file, 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        exclude=['auth.permission', 'contenttypes', 'sessions.session'],
        indent=2,
        stdout=f
    )

print(f"Data exported successfully to {output_file}")
