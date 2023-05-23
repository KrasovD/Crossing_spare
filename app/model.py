from app import db, login_manager
from datetime import datetime
from sqlalchemy import select, update
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

now = datetime.now()

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spare = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, default=now)


class Spare_parts(db.Model):
    id = db.Column(db.INTEGER, unique=True,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(300), nullable=True)
    article_number = db.Column(db.VARCHAR(150), nullable=True)
    another_info = db.Column(db.TEXT, nullable=True)
    brend = db.Column(db.VARCHAR(300), nullable=True)
    category = db.Column(db.VARCHAR(200), nullable=True)

class Available(db.Model):
    id = db.Column(db.INTEGER, unique=True,
                   primary_key=True, autoincrement=True)
    spare_parts_id = db.Column(db.ForeignKey('spare_parts.id'))
    count = db.Column(db.VARCHAR(100), nullable=True)
    price = db.Column(db.VARCHAR(100), nullable=True)
    location = db.Column(db.VARCHAR(100), nullable=True)
    data_update = db.Column(db.DATE)
    store = db.Column(db.VARCHAR(100), nullable=True)

class Crossing(db.Model):
    id = db.Column(db.INTEGER, unique=True,
                   primary_key=True, autoincrement=True)
    id_spare = db.Column(db.ForeignKey('spare_parts.id'))
    id_cross = db.Column(db.ForeignKey('spare_parts.id'))

class Parsing(db.Model):
    id = db.Column(db.INTEGER, unique=True,
                   primary_key=True, autoincrement=True)
    category = db.Column(db.VARCHAR(100), nullable=True)
    value = db.Column(db.VARCHAR(100), nullable=True)
    store = db.Column(db.VARCHAR(100), nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    date_update = db.Column(db.DATE, nullable=True)
    count_all = db.Column(db.INTEGER, nullable=True)
    count_success = db.Column(db.INTEGER, nullable=True)
try:
    db.create_all()
except:
    pass

