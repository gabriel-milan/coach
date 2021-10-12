import os

# This defines the base dir for all relative imports for our project, put the file in your root folder so the
# base_dir points to the root folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Since we only have one app which we use
INSTALLED_APPS = (
    'scoach',
)
