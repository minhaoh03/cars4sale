from . import db
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone

tz = timezone('EST')

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.String)
    region = db.Column(db.String)
    img = db.Column(db.String)
    resultsToImg = {}
    results = []
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(24), unique=True)
    password = db.Column(db.String(150), nullable=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    region = db.Column(db.String)
    area = db.Column(db.String)
    image = db.Column(db.String)
    title = db.Column(db.String)
    price = db.Column(db.String)
    link = db.Column(db.String)
    datePosted = db.Column(db.DateTime, default=datetime.now(tz))
    #userBook = db.relationship('User', backref=db.backref('car'))