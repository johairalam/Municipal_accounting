"""
Django settings for muni_account project.
"""

from pathlib import Path
import os
import pdfkit
import dj_database_url
LOGGING_CONFIG = None
LOGGING = {}
BASE_DIR = Path(__file__).resolve().parent.parent

# ========= SECURITY =========
CSRF_TRUSTED_ORIGINS = [
    "https://municipal-accounting.up.railway.app",
]

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-^b1eun5uhk!4mxq1o@w-6w39pgf^349a5d&kk++yjpw=22x*$m"
)

# Default to False in production; override locally if needed
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "municipal-accounting.up.railway.app",
]

# ========= APPS =========
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

# ========= MIDDLEWARE =========
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise for static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ========= URLS / WSGI =========
ROOT_URLCONF = "muni_account.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

# ========= DATABASE =========
# Railway: DATABASE_URL env (Postgres)
# Local: SQLite fallback
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# ========= AUTH / USER MODEL =========
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ========= I18N / TIME =========
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========= STATIC FILES =========
STATIC_URL = "/static/"

# One project-level static dir is enough; app static is auto-discovered
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Let WhiteNoise compress static files
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========= PDFKIT / WKHTMLTOPDF =========
USE_PDFKIT = os.environ.get("USE_PDFKIT", "True") == "True"

WKHTMLTOPDF_CMD = os.environ.get(
    "WKHTMLTOPDF_CMD",
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

PDFKIT_CONFIG = None
if USE_PDFKIT:
    try:
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
    except Exception:
        PDFKIT_CONFIG = None
