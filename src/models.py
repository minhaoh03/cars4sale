from . import db
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone

tz = timezone('EST')
    
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(24), unique=True)
    password = db.Column(db.String(150), nullable=False)
    
    favs = db.relationship('Car', backref=db.backref('user'))           # Linked to favorited cars in the Car model

class Car(db.Model):
    __tablename__= 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    region = db.Column(db.String)
    area = db.Column(db.String)
    image = db.Column(db.String)
    title = db.Column(db.String)
    price = db.Column(db.String)
    link = db.Column(db.String)
    datePosted = db.Column(db.DateTime, default=datetime.now(tz))
    
    favorited = db.Column(db.Integer, db.ForeignKey('users.id'))        # Linked to favs in User model