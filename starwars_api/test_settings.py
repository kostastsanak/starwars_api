from .settings import *

# Use SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Reduce password validation for tests
AUTH_PASSWORD_VALIDATORS = []

# Disable logging during tests
LOGGING = {}

# Use a simple cache backend for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable CORS checks in tests
CORS_ALLOW_ALL_ORIGINS = True
