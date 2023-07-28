from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from app.config import *
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
login_manager = LoginManager()
db = SQLAlchemy()
bootstrap = Bootstrap5()
#csrf = CSRFProtect()

def create_app():
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://crossing_db:{password_db}@localhost:5432/crossing_db"

    db.init_app(app)
    bootstrap.init_app(app)
    #csrf.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app.crosser import bp as crosser_bp
        from app.parser import bp as parser_bp
        from app.auth import bp as auth_bp
        from app.api import bp as api_bp
        app.register_blueprint(crosser_bp)
        app.register_blueprint(parser_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(api_bp)

        return app
