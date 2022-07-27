from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from os import path
import pycraigslist

db = SQLAlchemy()

DB_NAME = 'database.db'
SKEY = '6ac97b1378900b1b09b9f86710a8f2fd'
POSSTACKKEY = '52382ded2394b8158b1ae36a14adb9d7'

def createApp():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SECRET_KEY'] = SKEY
    db.init_app(app)
    
    from .pages import pages

    app.register_blueprint(pages, url_prefix='/')
    
    createDB(app)
    
    return app
    
def createAPI(app):
    api = Api(app)
    return api
    
def createDB(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
    return db
