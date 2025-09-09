from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-m@v3gx+&pfh_uz-xzb%gydbmj63+ol+cx=7g^qlft7r0%msc23"

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "core",
    "voting",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "starwars_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "starwars_api.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "starwars_db",
        "USER": "postgres",
        "PASSWORD": "tsanak",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Star Wars API',
    'DESCRIPTION': '''
    A comprehensive RESTful API for Star Wars characters, films, and starships with voting functionality.
    
    ## Features
    - **Characters**: Browse, search, and filter Star Wars characters
    - **Films**: Explore Star Wars movies with detailed information
    - **Starships**: Discover starship specifications and details
    - **Voting**: Vote for your favorite characters, films, and starships
    - **SWAPI Integration**: Populate data directly from the Star Wars API
    
    ## Search & Filtering
    - Use the `search` parameter for text-based searches
    - Use `ordering` parameter to sort results (add '-' prefix for descending)
    - Apply filters using query parameters
    
    ## Pagination
    - Results are paginated (10 items per page by default)
    - Use `page` and `page_size` parameters to navigate
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'TAGS': [
        {
            'name': 'Characters',
            'description': 'Star Wars characters - browse, search, and get details about people from the galaxy far, far away.'
        },
        {
            'name': 'Films',
            'description': 'Star Wars films - explore movies, episodes, and their details.'
        },
        {
            'name': 'Starships',
            'description': 'Star Wars starships - discover spaceships, their specifications, and technical details.'
        },
        {
            'name': 'Voting',
            'description': 'Vote for your favorites - cast votes and view voting statistics.'
        },
        {
            'name': 'SWAPI Integration',
            'description': 'Data management - populate and synchronize data from the Star Wars API.'
        },
    ]
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'starwars_api.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

