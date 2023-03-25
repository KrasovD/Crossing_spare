from crossing_app import app, db
from datetime import datetime

now = datetime.utcnow

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spare = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, default=now)

class Spare_parts(db.Model):
    id = db.Column(db.INTEGER, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(300), nullable=True)
    article_number = db.Column(db.VARCHAR(150), nullable=True)
    another_info = db.Column(db.TEXT, nullable=True)
    brend = db.Column(db.VARCHAR(300), nullable=True)
    category = db.Column(db.VARCHAR(200), nullable=True)

class Available(db.Model):
    id = db.Column(db.INTEGER, unique=True, primary_key=True, autoincrement=True)
    spare_parts_id = db.Column(db.ForeignKey('spare_parts.id'))
    count = db.Column(db.VARCHAR(100), nullable=True)
    price = db.Column(db.VARCHAR(100), nullable=True)
    location = db.Column(db.VARCHAR(100), nullable=True)
    data_update = db.Column(db.DATE)
    store = db.Column(db.VARCHAR(100), nullable=True)

    
try:
    with app.app_context():
        db.create_all()
except:
    pass

