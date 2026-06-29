from pathlib import Path

import environ  # type: ignore[import-untyped]

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    PORT=(int, 8000),
    FRONTEND_URL=(str, "http://localhost:5173"),
    DATABASE_URL=(str, ""),
    REDIS_URL=(str, ""),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    AI_PROVIDER=(str, "openai"),
    OPENAI_API_KEY=(str, ""),
    OPENAI_BASE_URL=(str, ""),
    ANTHROPIC_API_KEY=(str, ""),
    OPENAI_MODEL=(str, "gpt-4o"),
    ANTHROPIC_MODEL=(str, "claude-sonnet-4-20250514"),
    AI_TEMPERATURE=(float, 0.7),
    AI_MAX_TOKENS=(int, 2048),
    AUTH_REQUIRED=(bool, True),
    JWT_SIGNING_KEY=(str, ""),
)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-not-for-production")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

CORS_ALLOWED_ORIGINS = env.list("FRONTEND_URL", default=["http://localhost:5173"])
CORS_ALLOW_CREDENTIALS = False  # No cookie-based auth used; Bearer token auth only

# AI provider settings — must be explicitly read for getattr(settings, ...) to work
AI_PROVIDER = env("AI_PROVIDER")
OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_BASE_URL = env("OPENAI_BASE_URL")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
OPENAI_MODEL = env("OPENAI_MODEL")
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL")
AI_TEMPERATURE = env("AI_TEMPERATURE")
AI_MAX_TOKENS = env("AI_MAX_TOKENS")

INSTALLED_APPS = [
    "daphne",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "strawberry.django",
    "channels",
    "apps.campaigns",
    "apps.content",
    "apps.ai",
    "apps.reviews",
    "apps.ws",
    "apps.auth",
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



ROOT_URLCONF = "config.urls"

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

ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = env("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": env.db()}
elif env("DB_HOST", default=None):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", default="acme"),
            "USER": env("DB_USER", default="postgres"),
            "PASSWORD": env("DB_PASSWORD", default="postgres"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

STRAWBERRY_GRAPHQL = {
    "SCHEMA": "config.schema.schema",
}
