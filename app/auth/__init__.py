from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix=True)

from . import views


