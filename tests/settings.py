SECRET_KEY = 'test_key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = [
    'composite_field',
    'tests',
]
