import os
import sys
sys.path.append('/home/websites/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Floodlight.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
