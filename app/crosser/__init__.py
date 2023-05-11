from flask import Blueprint

bp = Blueprint('crosser', __name__, template_folder='templates')
from app.crosser import crosser