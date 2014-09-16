"""
WSGI jelfig for jelf project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'calendar/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
os.environ["DJANGO_SETTINGS_MODULE"] = "calendar.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
