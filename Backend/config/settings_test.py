"""Aisla la suite automatizada de cualquier base de datos externa."""

import os

os.environ['DATABASE_URL'] = ''

from .settings import *  # noqa: F403


DATABASE_URL = ''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
