web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn muni_account.wsgi:application --bind 0.0.0.0:8000
