from config.settings.base import env

from .base import *  # noqa: F403

AUTH_REQUIRED = True  # Always enforce auth in production

DEBUG = False

if not DATABASE_URL:  # noqa: F405
    raise RuntimeError("DATABASE_URL is required in production")

_insecure_key = "insecure-dev-key-not-for-production"
if _insecure_key == SECRET_KEY:  # noqa: F405
    raise RuntimeError("DJANGO_SECRET_KEY must be set to a unique value in production")

_jwt_key = env("JWT_SIGNING_KEY")
if not _jwt_key:
    raise RuntimeError(
        "JWT_SIGNING_KEY must be set separately from DJANGO_SECRET_KEY in production"
    )

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [env("REDIS_URL", default="redis://localhost:6379")]},  # type: ignore[dict-item]
    },
}
