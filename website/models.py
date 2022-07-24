from . import db
from sqlalchemy.sql import func

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    results = []