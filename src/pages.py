import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
import requests
from . import db

#Flask login
from flask_login import login_required, login_user, logout_user, current_user

#For password hashes
from werkzeug.security import generate_password_hash, check_password_hash

#Result Models
from .models import Result, User

#Position Stack Key API
from .__init__ import POSSTACKKEY

#Image
import http.client, urllib.parse    
from bs4 import BeautifulSoup

#Craigslist API
import pycraigslist

pages = Blueprint('pages', __name__)    

stateMap = {'Alabama' : ['bham', 'mobile', 'montgomery', 'huntsville', 'tuscaloosa', 'auburn', 'dothan', 'gadsden', 'shoals'],
            'Alaska' : ['anchorage', 'juneau', 'fairbanks', 'kenai'],
            'Arizona' : ['phoenix', 'tucson', 'flagstaff', 'yuma', 'prescott', 'sierravista', 'mohave', 'showlow'],
            'Arkansas' : ['littlerock', 'fayar', 'fortsmith', 'texarkana', 'jonesboro'],
            'California' : ['sfbay', 'losangeles', 'sandiego', 'sacramento', 'fresno', 'santabarbara', 'bakersfield', 'modesto', 'stockton', 'monterey', 'orangecounty', 'inlandempire', 'chico', 'redding', 'humboldt', 'slo', 'montgomery', 'ventura', 'palmsprings', 'merced', 'lawrence', 'goldcountry', 'mendocino', 'imperial', 'yubasutter', 'susanville', 'siskiyou', 'hanford', 'santamaria'],
            'Colorado' : ['denver', 'cosprings', 'fortcollins', 'rockies', 'pueblo', 'boulder', 'westslope', 'eastco'],
            'Connecticut' : ['hartford', 'newhaven', 'newlondon', 'nwct'],
            'Delaware' : ['delaware'],
            'Florida' : ['fortlauderdale', 'miami', 'westpalmbeach', 'tampa', 'orlando', 'fortmyers', 'pensacola', 'gainesville', 'sarasota', 'daytona', 'keys', 'spacecoast', 'treasure', 'ocala', 'lakeland', 'staugustine', 'panamacity', 'lakecity', 'cfl', 'okaloosa'],
            'Georgia' : ['atlanta', 'savannah', 'augsuta', 'macon', 'athensga', 'columbusga', 'valdosta', 'brunswick', 'statesboro', 'nwga', 'albanyga'],
            'Hawaii' : ['honolulu'],
            'Idaho' : ['boise', 'eastidaho', 'twinfalls', 'lewiston'],
            'Illinois' : ['chicago', 'chambana', 'rockford', 'springfieldil', 'peoria', 'bn', 'carbondale', 'decatur', 'quincy', 'lasalle', 'mattoon'],
            'Indiana' : ['indianapolis', 'fortwayne', 'evansville', 'southbend', 'bloomington'],
            'Iowa' : ['desmoines', 'quadcities', 'iowacity', 'cedarrapids', 'siouxcity', 'dubuque', 'ames', 'waterloo', 'ottumwa', 'masoncity', 'fortdodge'],
            'Kansas' : ['wichita', 'topeka', 'lawrence', 'ksu', 'swks', 'nwks', 'seks', 'salina'],
            'Kentucky' : ['tucson', 'lexington', 'bgky','westky', 'owensboro', 'eastky'],
            'Louisiana' : ['neworleans', 'batonrouge', 'savannah', 'lafayette', 'lakecharles', 'monroemi', 'houma', 'cenla'],
            'Maine' : ['maine'],
            'Maryland' : ['baltimore', 'easternshore', 'westmd', 'annapolis', 'smd', 'frederick'],
            'Massachussetts' : ['boston', 'westernmass', 'capecod', 'worcester', 'southcoast'],
            'Michigan' : ['detroit', 'grandrapids', 'annarbor', 'lansing', 'flint', 'saginaw', 'kalamazoo', 'up', 'nmi', 'jxn', 'centralmich', 'muskegon', 'janesville', 'swmi', 'thumb', 'battlecreek', 'monroe', 'holland'],
            'Minnesota' : ['minneapolis', 'duluth', 'rmn', 'stcloud', 'mankato', 'bemidji', 'brainerd', 'marshall'],
            'Mississippi' : ['jackson', 'gulfport', 'hattiesburg', 'northmiss', 'meridian', 'natchez'],
            'Missouri' : ['stlouis', 'kansascity', 'springfield', 'columbiamo', 'joplin', 'semo', 'stjoseph', 'loz', 'kirksville'],
            'Montana' : ['montana', 'missoula', 'billings', 'bozeman', 'helena', 'greatfalls', 'butte', 'kalispell'],
            'Nebraska' : ['omaha', 'lincoln', 'grandisland', 'northplatte', 'scottsbluff'],
            'Nevada' : ['lasvegas', 'reno', 'elko'],
            'New Hampshire' : ['nh'],
            'New Jersey' : ['newjersey', 'southjersey', 'cnj', 'jerseyshore'],
            'New Mexico' : ['albuquerque', 'santafe', 'lascruces', 'roswell', 'farmington', 'clovis'],
            'New York' : ['newyork', 'buffalo', 'albany', 'rochester', 'syracuse', 'ithaca', 'utica', 'binghamton', 'hudsonvalley', 'longisland', 'watertown', 'plattsburgh', 'catskills', 'chautauqua', 'elmira', 'potsdam', 'oneonta', 'fingerlakes', 'glensfalls', 'twintiers'],
            'North Carolina' : ['raleigh', 'charlotte', 'greensboro', 'asheville', 'winstonsalem', 'fayetteville', 'wilmington', 'eastnc', 'outerbanks', 'boone', 'hickory', 'onslow'],
            'South Carolina' : ['columbia', 'charleston', 'greenville', 'myrtlebeach', 'hiltonhead', 'florencesc'],
            'Ohio' : ['cleveland', 'cincinnati', 'columbus', 'dayton', 'toledo', 'akroncanton', 'youngstown', 'mansfield', 'limaohio', 'athensohio', 'sandusky', 'ashtabula', 'chillicothe', 'zanesville', 'tuscarawas'],
            'Oklahoma' : ['oklahomacity', 'tulsa', 'lawton', 'stillwater', 'enid'],
            'Oregon' : ['portland', 'eugene', 'medford', 'salem', 'bend', 'oregoncoast', 'eastoregon', 'corvallis', 'roseburg', 'klamath'],
            'Pennsylvania' : ['philadelphia', 'pittsburgh', 'harrisburg', 'allentown', 'erie', 'scranton', 'pennstate', 'reading', 'lancaster', 'altoona', 'poconos', 'york', 'williamsport', 'chambersburg', 'meadville'],
            'Rhode Island' : ['providence'],
            'South Carolina' : ['columbia', 'charleston', 'greenville', 'myrtlebeach', 'hiltonhead', 'florencesc'],
            'South Dakota' : ['sd', 'siouxfalls', 'rapidcity', 'csd', 'nesd'],
            'Tennessee' : ['nashville', 'memphis', 'knoxville', 'chattanooga', 'tricities', 'clarksville', 'jacksontn', 'cookeville'],
            'Texas' : ['austin', 'dallas', 'houston', 'sanantonio', 'elpaso', 'mcallen', 'beaumont', 'corpuschristi', 'brownsville', 'lubbock', 'odessa', 'amarillo', 'waco', 'laredo', 'easttexas', 'collegestation', 'killeen', 'abilene', 'wichitafalls', 'sanmarcos', 'galveston', 'victoriatx', 'nacogdoches', 'sanangelo', 'delrio', 'bigbend', 'texoma'],
            'Utah' : ['saltlakecity', 'provo', 'ogden', 'stgeorge', 'logan'],
            'Vermont' : ['burlington'],
            'Virginia' : ['norfolk', 'richmond', 'roanoke', 'charlottesville', 'blacksburg', 'lynchburg', 'danville', 'harrisonburg', 'fredericksburg', 'winchester', 'swva'],
            'Washington' : ['seattle', 'spokane', 'bellingham', 'yakima', 'kpr', 'wenatchee', 'pullman', 'skagit', 'olympic', 'moseslake'],
            'West Virginia' : ['wv', 'charlestonwv', 'morgantown', 'parkersburg', 'huntington', 'wheeling', 'martinsburg', 'swv'],
            'Wisconsin' : ['wilwaukee', 'madison', 'greenbay', 'eauclaire', 'appleton', 'lacrosse', 'wausau', 'racine', 'janesville', 'sheboygan', 'northernwi'],
            'Wyoming' : ['wyoming'],
            'District of Columbia' : ['washingtondc'],
            }

def getLocation(ip):                    # Location getter of an ip address
    response = requests.get("http://ip-api.com/json/{}?fields=regionName".format(ip))
    js = response.json()
    return js


@pages.route('/', methods=['POST','GET'])                       # Home Page
def homepage():
    ip = request.environ['REMOTE_ADDR']  
    
    if request.method == 'POST':  
        location = getLocation(ip)

        region = location.get('regionName')
        
        postedSearch = request.form.get('search')      
        return redirect(url_for('pages.results', search=postedSearch, region=region))
    return render_template('homepage.html', ip=ip)

@pages.route('/results', methods=['POST','GET'])                    # Results Page
def results():
    newResult = Result()
    newResult.results.clear()
    
    newResult.search = request.args.get('search')
    newResult.region = request.args.get('region')

    for city in stateMap.get(newResult.region):
        cars = pycraigslist.forsale.cta(site=city, query=newResult.search)     
        for car in cars.search(limit=1):
            carURL = car.get('url')
            carTitle = car.get('title')
            carPrice = car.get('price')
            soup = BeautifulSoup(requests.get(carURL).text, 'html.parser')
            allImgs = soup.find('img')
            if allImgs is not None and not carTitle in newResult.resultsToImg and carPrice != '$0':     #If there is an image, not a replicate, and the price is not 0, show the result on the webpage
                img = soup.find('img')['src']
                newResult.resultsToImg[carTitle] = img
                newResult.results.append(car)
            print(car)
    return render_template('results.html', Result=newResult)
                    
@pages.route('/aboutus', methods=['GET'])                           # About Us Page
def aboutus():
    return render_template('aboutus.html')

@pages.route('/profile', methods=['POST','GET'])                # Profile Page
@login_required
def profile():
    if request.method == 'GET':
        pass
    return render_template('profile.html', user=current_user)

@pages.route('/register', methods=['POST','GET'])                           # Register Page
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pw')
        confpassword = request.form.get('confpw')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email already exists.', category='ERROR')
        elif len(email) < 4:
            flash('Invalid Email: Email must be greater than 4 characters.', category='ERROR')
        elif len(password) < 6:
            flash('Invalid Password: Password must be at least 6 or more characters.', category='ERROR')
        elif password != confpassword:
            flash('Invalid Confirmation: Passwords do not match.', category='ERROR')
        else:
            newUser = User(email=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser)
            flash('Account created!', category='SUCCESS')
            return redirect(url_for('pages.homepage'))
    return render_template('register.html')

@pages.route('/login', methods=['POST','GET'])                      # Login Page
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pw')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='SUCCESS')
                login_user(user, remember=True)
                return redirect(url_for('pages.homepage'))
            else:
                flash('Incorrect Password', category='ERROR')
        else:
            flash('No user with that email', category='ERROR')
    return render_template('login.html')

@pages.route('/logout', methods=['GET'])                        # Logout Page
def logout():           
    if not current_user.is_authenticated:
        flash('You are not logged in', category='message')
    else:
        logout_user()
        flash('Successfully Logged Out!', category='SUCCESS')
    return redirect(url_for('pages.homepage'))