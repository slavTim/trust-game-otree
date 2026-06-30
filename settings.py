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
    'allow_incomplete_groups': True,
}
SESSION_CONFIGS = [
    dict(
        name='trust_without_bot',
        display_name="Trust Game (без бота)",
        num_demo_participants=8,
        app_sequence=['trust'],
        use_bot=False,
    ),
    dict(
        name='trust_with_bot',
        display_name="Trust Game (с ботом)",
        num_demo_participants=8,
        app_sequence=['trust'],
        use_bot=True,
    ),
]


INSTALLED_APPS = ['otree']
ROOMS = [
    dict(
        name='trust_lab',
        display_name='Лаборатория доверия (Trust Lab)',
    ),
]
OTREE_PRODUCTION = False

OTREE_AUTH_LEVEL = 'demo'
#ALLOW_INCOMPLETE_GROUPS = True
ROOT_URLCONF = 'trust_game.urls'