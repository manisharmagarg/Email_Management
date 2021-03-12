from flask_bcrypt import Bcrypt
from flask import Flask, redirect, request, session, render_template, \
    url_for, jsonify
from flask.logging import *
import os
from dotenv import load_dotenv
from pathlib import Path

app = Flask(__name__)
bcrypt = Bcrypt(app)

BASE_DIR = Path(__file__).resolve().parent.parent

env_path = os.path.join(BASE_DIR, '.env')

load_dotenv(dotenv_path=env_path, verbose=True)

app.config['secretkey'] = 'some-strong+secret#key'
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

app.config.update(
    CELERY_BROKER_URL='amqp://guest@localhost//',
    CELERY_RESULT_BACKEND='rpc://localhost//'
)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'anaconda.wb@gmail.com'
app.config['MAIL_PASSWORD'] = 'weave@anaconda'

app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

from emailapp import routes
