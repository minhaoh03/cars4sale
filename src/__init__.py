from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from os import path
import pycraigslist
from flask_login import LoginManager

db = SQLAlchemy()

###### IMPORTANT AND SECRET VARIABLES/KEYS FOR THE WEBSITE ######
DB_NAME = 'database.db'
SKEY = '6ac97b1378900b1b09b9f86710a8f2fd'
POSSTACKKEY = '52382ded2394b8158b1ae36a14adb9d7'
#################################################################

def createApp():
    # Create app
    app = Flask(__name__)

    # Config database location
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Config secret key for website
    app.config['SECRET_KEY'] = SKEY
    
    # Initailize the database for the app
    db.init_app(app)
    
    from .pages import pages

    # Register all the pages for the website
    app.register_blueprint(pages, url_prefix='/')
    
    # Start the login manager
    login_manager = LoginManager()
    login_manager.login_view = 'pages.login'
    login_manager.init_app(app)
    
    # Create the DB for the app
    createDB(app)
    
    from .models import User
    
    # User loader 
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

### API Creator ###
def createAPI(app):
    api = Api(app)
    return api
    
    
### Database Creator ###
def createDB(app):
    if not path.exists('src/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
    return db
