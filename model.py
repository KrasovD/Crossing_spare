from app import db, app
import datetime

now = datetime.datetime.utcnow

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spare = db.Column(db.String, unique=True, nullable=False)
    datetime = db.Column(db.DateTime, default=now)
try:
    with app.app_context():
        db.create_all()
except:
    pass
