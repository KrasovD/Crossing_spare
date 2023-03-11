from crossing_app import app, db
from datetime import datetime

now = datetime.utcnow

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spare = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, default=now)

class Autokontinent(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    article_number = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    name = db.Column(db.Text, nullable=True)
    brend = db.Column(db.String(50), nullable=True)
    count = db.Column(db.String(50), nullable=True)
    price = db.Column(db.String(50), nullable=True)
    another_info = db.Column(db.Text, nullable=True)
    

class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_number = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    name = db.Column(db.Text, nullable=True)
    brend =  db.Column(db.String(50), nullable=True)
    count = db.Column(db.String(50), nullable=True)
    price = db.Column(db.String(50), nullable=True)
    another_info = db.Column(db.Text, nullable=True) 


class Autoopt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_number = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    name = db.Column(db.Text, nullable=True)
    brend = db.Column(db.String(50), nullable=True)
    count = db.Column(db.String(50), nullable=True)
    price = db.Column(db.String(50), nullable=True)
    another_info = db.Column(db.Text, nullable=True)
    
try:
    with app.app_context():
        db.create_all()
except:
    pass

