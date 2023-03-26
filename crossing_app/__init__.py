from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from crossing_app.config  import *

app = Flask(__name__)
bootstrap = Bootstrap5(app)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://crossing_db:{password_db}@localhost:5432/crossing_db"
db.init_app(app)


import crossing_app.views