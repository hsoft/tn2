import os

import local_settings

ADMINS = [("Virgil Dupras", 'hsoft@hardcoded.net')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS

# Application definition

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

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'post_office.EmailBackend'
    if getattr(local_settings, 'EMAIL_HOST'):
        EMAIL_HOST = local_settings.EMAIL_HOST
        EMAIL_PORT = local_settings.EMAIL_PORT
        EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
        EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
        EMAIL_USE_TLS = local_settings.EMAIL_USE_TLS


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = local_settings.DATABASES

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

STATIC_ROOT = os.path.join(local_settings.PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(local_settings.PROJECT_ROOT, 'media')
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
    'SASS_BINARY': '/usr/bin/env {}'.format(os.path.join(local_settings.PROJECT_ENVPATH, 'bin', 'sassc')),
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
