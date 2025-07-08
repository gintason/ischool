# teachers/__init__.py
from __future__ import absolute_import, unicode_literals

# Import Celery application instance
from iSchool_Ola.celery import app as celery_app

__all__ = ('celery_app',)
