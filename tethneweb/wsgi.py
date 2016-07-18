"""
WSGI config for django_tethne project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

try:
    sys.path.append('/etc')
    from tethne_conf import DJANGO_SECRET_KEY
    os.environ['DJANGO_SECRET_KEY'] = DJANGO_SECRET_KEY
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethneweb.settings")

application = get_wsgi_application()
