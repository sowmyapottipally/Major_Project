import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShortTextSentimentClassification.settings')

# Temporarily modify settings to exclude appuser
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'accounts',
    ],
    SECRET_KEY='temp-key',
)

django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superuser 'admin' created with password 'admin'")
else:
    user = User.objects.get(username='admin')
    user.set_password('admin')
    user.save()
    print("Password for 'admin' updated to 'admin'")