from .settings import *


from dotenv import load_dotenv

# Load environment variables
load_dotenv("./env_docker.env")


MEDIA_ROOT = "/code_volume/media_root"
DIABETIC_FOOT_AI_ENABLED = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/code_volume/db_docker.sqlite3',
    }
}
