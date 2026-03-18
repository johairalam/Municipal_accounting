"""
Django settings for muni_account project.
"""
USE_WEASYPRINT = os.environ.get("USE_WEASYPRINT", "True") == "True"
from pathlib import Path
import os
import pdfkit
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-me"  # used only locally if env not set
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

# For now allow all; later restrict to your Railway domain
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "muni_account.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "muni_account.wsgi.application"

# DATABASE: local = sqlite (if no env), Railway = DATABASE_URL (Postgres)
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3"
    )
}

# Custom user
AUTH_USER_MODEL = "accounts.User"

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

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "static")
if (BASE_DIR / "accounts" / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "accounts" / "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# pdfkit / wkhtmltopdf
# On Railway, WKHTMLTOPDF_CMD will not exist, so we make this optional.
USE_PDFKIT = os.environ.get("USE_PDFKIT", "True") == "True"

WKHTMLTOPDF_CMD = os.environ.get(
    "WKHTMLTOPDF_CMD",
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"  # local Windows default
)

PDFKIT_CONFIG = None
if USE_PDFKIT:
    try:
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
    except Exception:
        PDFKIT_CONFIG = None
