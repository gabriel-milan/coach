from .base import *

# This is not a secret!!!
SECRET_KEY = 'thisisnotasecret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
