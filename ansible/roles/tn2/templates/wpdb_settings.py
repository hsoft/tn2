DATABASES = {
    'wordpress': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{{ tn2_wp_dbname }}',
        'USER': '{{ django_dbuser }}',
        'PASSWORD': '{{ django_dbpass }}',
        'HOST': 'localhost',
    }
}

