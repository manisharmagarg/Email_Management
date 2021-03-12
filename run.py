import subprocess

run = 'celery -A tasks.tasks.app worker -B --loglevel=info -Q default,send_email -c 10'
e = '%s' % run
subprocess.call(e, shell=True)

