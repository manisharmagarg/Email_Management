web: gunicorn manage:app
worker: celery -A tasks.tasks.app worker -B --loglevel=info -Q default,send_email -c 10