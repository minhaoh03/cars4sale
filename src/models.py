from . import db
from flask_login import UserMixin

class Car():
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    region = db.Column(db.String)
    area = db.Column(db.String)
    title = db.Column(db.String)
    price = db.Column(db.String)
    link = db.Column(db.String)
    yearPosted = db.Column(db.Integer)
    monthPosted = db.Column(db.Integer)
    dayPosted = db.Column(db.Integer)
    hourPosted = db.Column(db.Integer)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.String)
    region = db.Column(db.String)
    img = db.Column(db.String)
    resultsToImg = {}
    results = []

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    region = db.Column(db.String)
    area = db.Column(db.String)
    title = db.Column(db.String)
    price = db.Column(db.String)
    link = db.Column(db.String)
    yearPosted = db.Column(db.Integer)
    monthPosted = db.Column(db.Integer)
    dayPosted = db.Column(db.Integer)
    hourPosted = db.Column(db.Integer)
    
    
    
    