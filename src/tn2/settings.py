import os
from pathlib import Path
import json

HERE = Path(__file__).parent
SRC_ROOT = HERE.parent
CONF_PATH = Path(os.environ['TN2_CONF_PATH'])

# Start with parsing the conf.json file

with CONF_PATH.open('rt') as fp:
    json_conf = json.load(fp)

if json_conf.get('project_root'):
    PROJECT_ROOT = Path(json_conf['project_root'])
else:
    PROJECT_ROOT = SRC_ROOT.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
    },
}
DATABASES['default'].update(json_conf['database'])
SECRET_KEY = json_conf['secret_key']
DEBUG = json_conf.get('debug', False)
READONLY = json_conf.get('readonly', False)
ALLOWED_HOSTS = json_conf.get('allowed_hosts', [])

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'post_office.EmailBackend'
    if json_conf.get('email'):
        EMAIL_HOST = json_conf['email']['host']
        EMAIL_PORT = json_conf['email']['port']
        EMAIL_HOST_USER = json_conf['email']['email']
        EMAIL_HOST_PASSWORD = json_conf['email']['password']
        EMAIL_USE_TLS = True

# And now, let's define the rest of our settings

PROJECT_ENVPATH = PROJECT_ROOT.joinpath('env')

ADMINS = [("Virgil Dupras", 'hsoft@hardcoded.net')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'registration',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.postgres',

    'post_office',
    'ckeditor',
    'ckeditor_uploader',
    'captcha',

    'tn2app.apps.Tn2AppConfig',
]

COMMENT_MAX_LENGTH = 10000

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tn2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [SRC_ROOT.joinpath('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tn2app.context_processors.inject_settings',
                'tn2app.context_processors.fromfr',
            ],
        },
    },
]


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'hashers_passlib.phpass',
]
# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True

USE_TZ = False

SITE_ID = 1

LOGIN_REDIRECT_URL = 'homepage'
LOGOUT_REDIRECT_URL = 'homepage'
AUTHENTICATION_BACKENDS = ['tn2app.auth_backends.EmailAuthenticationBackend']
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_FORM = 'tn2app.forms.user.SignupForm'
DEFAULT_FROM_EMAIL = 'info@threadandneedles.fr'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = str(PROJECT_ROOT.joinpath('static'))
STATIC_URL = '/static/'

MEDIA_ROOT = str(PROJECT_ROOT.joinpath('media'))
MEDIA_URL = json_conf.get('media_url', '/media/')
THUMBNAIL_URL = json_conf.get('thumbnail_url', '/thumb/')

# Host to redirect to when we hit missing media in DEBUG mode (see serve_* debug views)
MEDIA_DEBUG_REDIRECT_TO = 'https://images.threadandneedles.org'

# Logging

if json_conf.get('log_to'):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(asctime)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': json_conf.get('log_to'),
                'formatter': 'simple',
            }
        },
        'loggers': {
            'tn2app': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': True,
            }
        },
    }

# Others

CKEDITOR_JQUERY_URL = 'https://code.jquery.com/jquery-2.2.4.min.js'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format'],
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'Undo', 'Redo'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['NumberedList', 'BulletedList', 'HorizontalRule'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Smiley', 'SpecialChar'],
            ['Source'],
        ],
        'format_tags': 'p;h2;h3;h4;h5;h6;pre',
        'disableNativeSpellChecker': False,
        'width': '100%',
        'extraPlugins': 'justify,horizontalrule',
    },
    'restricted': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'Undo', 'Redo'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Smiley', 'SpecialChar'],
            ['Source'],
        ],
        'disableNativeSpellChecker': False,
        'width': '100%',
        'height': '200',
    },
}

THUMBNAIL_ALIASES = {
    '': {
        'preview': {'size': (300, 200)},
        'avatar': {'size': (34, 34)},
        'avatar-big': {'size': (60, 60)},
        'avatar-bigger': {'size': (80, 80)},
        'group-avatar': {'size': (80, 80)},
        'group-avatar-big': {'size': (150, 150)},
        'project-list': {'size': (180, 180), 'external': True},
        'project-alternate-view': {'size': (50, 50), 'external': True},
    }
}

DISCUSSION_PAGINATE_BY = 15

CAPTCHA_CHALLENGE_FUNCT = 'tn2app.captcha.numerical_string_challenge'
