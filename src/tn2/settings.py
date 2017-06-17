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
ALLOWED_HOSTS = json_conf.get('allowed_hosts', [])

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'post_office.EmailBackend'
    if json_conf.get('email'):
        EMAIL_HOST = json_conf['email']['HOST']
        EMAIL_PORT = json_conf['email']['PORT']
        EMAIL_HOST_USER = json_conf['email']['HOST_USER']
        EMAIL_HOST_PASSWORD = json_conf['email']['HOST_PASSWORD']
        EMAIL_USE_TLS = json_conf['email']['USE_TLS']

# And now, let's define the rest of our settings

PROJECT_ENVPATH = PROJECT_ROOT.joinpath('env')

ADMINS = [("Virgil Dupras", 'hsoft@hardcoded.net')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.postgres',

    'post_office',
    'account',
    'ckeditor',
    'ckeditor_uploader',
    'easy_thumbnails',
    'pipeline',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.account',
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

LOGIN_URL = 'account_login'
LOGOUT_REDIRECT_URL = 'homepage'
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_HOOKSET = 'tn2app.account_hookset.AccountHookset'
AUTHENTICATION_BACKENDS = ['account.auth_backends.EmailAuthenticationBackend']
DEFAULT_FROM_EMAIL = 'info@threadandneedles.fr'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

STATIC_ROOT = str(PROJECT_ROOT.joinpath('static'))
STATIC_URL = '/static/'

MEDIA_ROOT = str(PROJECT_ROOT.joinpath('media'))
MEDIA_URL = '/media/'

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
        'preview': {'size': (300, 200), 'crop': True},
        'avatar': {'size': (34, 34), 'crop': True},
        'avatar-big': {'size': (60, 60), 'crop': True},
        'avatar-bigger': {'size': (80, 80), 'crop': True},
        'group-avatar': {'size': (80, 80), 'crop': True},
        'group-avatar-big': {'size': (150, 150), 'crop': True},
        'project-list': {'size': (180, 180), 'crop': True},
        'project-alternate-view': {'size': (50, 50), 'crop': True},
    }
}

PIPELINE = {
    'CSS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'COMPILERS': [
        'pipeline.compilers.sass.SASSCompiler',
    ],
    'SASS_BINARY': '/usr/bin/env {}'.format(str(PROJECT_ENVPATH.joinpath('bin', 'sassc'))),
    'STYLESHEETS': {
        'main': {
            'source_filenames': [
                'sass/main.scss',
            ],
            'output_filename': 'css/main.css',
        },
    },
    'JAVASCRIPT': {
    },
}

# Others

DISCUSSION_PAGINATE_BY = 15

CAPTCHA_CHALLENGE_FUNCT = 'tn2app.captcha.numerical_string_challenge'
