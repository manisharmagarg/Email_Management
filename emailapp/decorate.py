from functools import wraps
from flask import redirect, render_template
from emailapp import *


def login_required(required_login):
    @wraps(required_login)
    def decorated(*args, **kwargs):
        try:
            user = session['email']
            user_id = session['user']
            request.user = user_id
        except:
            return redirect('login')
        return required_login(*args, **kwargs)
    return decorated
