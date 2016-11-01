from pathlib import Path

DEBUG = True
HERE = Path(__file__).parent
PROJECT_ROOT = str(HERE.parent)
PROJECT_ENVPATH = str(HERE.parent.joinpath('env'))
PROJECT_DOMAIN = '*'
SECRET_KEY = '2#i^!$#$3mcmlttfabck(o2q-$#iil^%hds=r65+^$c++0si&u'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(HERE.joinpath('sqlite.db')),
    }
}
