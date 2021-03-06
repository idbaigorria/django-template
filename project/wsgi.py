"""
WSGI config for django_template project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys
import site

PROJECT_DIR=os.path.abspath(os.path.dirname(__file__))
ROOT_DIR=os.path.dirname(PROJECT_DIR)

sys.path.extend([PROJECT_DIR, ROOT_DIR])

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "project.settings")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

from django.conf import settings

if settings.DEBUG:
    import uwsgi
    from uwsgidecorators import timer
    from django.utils import autoreload

    @timer(3)
    def change_code_gracefull_reload(sig):
        if autoreload.code_changed():
            uwsgi.reload()
