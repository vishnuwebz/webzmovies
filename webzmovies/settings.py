"""
Django settings for webzmovies project (updated for Render / prod).

Keep secrets (SECRET_KEY, DATABASE_URL, etc.) in environment variables.
"""

import os
from pathlib import Path
import dj_database_url

# Base dir
BASE_DIR = Path(__file__).resolve().parent.parent

# ---- Security / env flags ----
# Put a real secret in env for production. The fallback below is ONLY for local/dev.
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-ufrq$_dkp30!q%6e&@lg=hodlo7bpu2y3yoe&i^00@ijh%)be("
)

# DEBUG should be False in production. Set DEBUG=true in your dev environment only.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ALLOWED_HOSTS - default includes localhost and a Render default domain
DEFAULT_ALLOWED = "127.0.0.1,localhost,webzmovies.onrender.com"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED).split(",")

# CSRF trusted origins - include your production domain(s)
DEFAULT_CSRF = "http://127.0.0.1,http://localhost,https://webzmovies.onrender.com"
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", DEFAULT_CSRF).split(",")

# ---- Installed apps / middleware ----
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # your apps
    "movies.apps.MoviesConfig",
    "accounts",

    # allauth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static files

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SITE_ID = int(os.getenv("SITE_ID", "1"))

# Authentication backends (keep ModelBackend first for login() defaults)
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ROOT_URLCONF = "webzmovies.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "webzmovies.wsgi.application"

# ---- Database configuration ----
# Use DATABASE_URL in production (Render will provide DATABASE_URL if you add a Postgres service)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)}
else:
    # default local sqlite (development)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---- Password validators ----
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---- Static / Media ----
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # required by collectstatic
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Security behind proxies (Render)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Auth redirects ----
LOGIN_URL = "movies:login"
LOGIN_REDIRECT_URL = "movies:home"
LOGOUT_REDIRECT_URL = "movies:home"

# ---- django-allauth (modern settings) ----
# Replace deprecated settings: use ACCOUNT_LOGIN_METHODS & ACCOUNT_SIGNUP_FIELDS
ACCOUNT_LOGIN_METHODS = {"username", "email"}  # supports login by username or email
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
# Keep email verification optional by default, but override via env if needed
ACCOUNT_EMAIL_VERIFICATION = os.getenv("ACCOUNT_EMAIL_VERIFICATION", "optional")
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# ---- Email configuration (dev default) ----
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@localhost")
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# ---- Twilio / 3rd-party (keep secrets in env) ----
# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Extra convenience: you can set ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS in env
# e.g. ALLOWED_HOSTS=127.0.0.1,localhost,webzmovies.onrender.com
# CSRF_TRUSTED_ORIGINS=https://webzmovies.onrender.com

# End of settings.py
