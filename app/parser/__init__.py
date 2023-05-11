from flask import Blueprint

bp = Blueprint('parser', __name__, template_folder='templates')


from app.parser import parser