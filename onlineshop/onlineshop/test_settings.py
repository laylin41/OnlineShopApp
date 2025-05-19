from .settings import *

DATABASES['default']['NAME'] = 'test_neondb'
DATABASES['default']['TEST'] = {
    'MIRROR': 'default',
}

