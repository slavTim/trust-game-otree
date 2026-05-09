import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
USE_POINTS = True
LANGUAGE_CODE = 'ru'

SECRET_KEY = 'dummy-key-12345'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 1.00,
    'participation_fee': 0.00,
    'doc': "",
}

SESSION_CONFIGS = [
    {
        'name': 'trust',
        'display_name': "Trust Game",
        'num_demo_participants': 2,
        'app_sequence': ['trust'],
    },
]

INSTALLED_APPS = ['otree']
ROOMS = []
OTREE_PRODUCTION = False

OTREE_AUTH_LEVEL = 'demo'
