from . import db
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone

tz = timezone('EST')
    
userCarTable = db.Table('userCarIdentifier',
    db.Column('userID', db.Integer, db.ForeignKey('users.userID')),
    db.Column('carID', db.Integer, db.ForeignKey('cars.carID'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    userID = db.Column(db.Integer, primary_key=True)
    userUsername = db.Column(db.Integer, unique=True)
    userEmail = db.Column(db.String(150), unique=True, nullable=False)
    userPassword = db.Column(db.String(150), nullable=False)
    
    favs = db.relationship('Car', secondary=userCarTable, backref=db.backref('user'))           # Linked to favorited cars in the Car model
    
    def get_id(self):
        return self.userID

class Car(db.Model):
    __tablename__= 'cars'
    
    carID = db.Column(db.Integer, primary_key=True)
    carCountry = db.Column(db.String)
    carRegion = db.Column(db.String)
    carArea = db.Column(db.String)
    carImage = db.Column(db.String)
    carTitle = db.Column(db.String)
    carPrice = db.Column(db.String)
    carLink = db.Column(db.String)
    carDatePosted = db.Column(db.DateTime, default=datetime.now(tz))
    
    def get_id(self):
        return self.carID