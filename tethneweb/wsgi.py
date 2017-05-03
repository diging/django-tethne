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
