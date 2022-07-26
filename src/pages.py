import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
import requests

#DB import
from . import db

#Flask login
from flask_login import login_required, login_user, logout_user, current_user

#For password hashes
from werkzeug.security import generate_password_hash, check_password_hash

#Result Models
from .models import User, Car

#Position Stack Key API
from .__init__ import POSSTACKKEY

#Image 
from bs4 import BeautifulSoup

#Craigslist API
import pycraigslist

#Time
from datetime import datetime, timedelta
from pytz import timezone

########################################## PAGE BLUEPRINT ##############################################
pages = Blueprint('pages', __name__)    


### Craigslist State to Site Map !!!! FOR US ONLY SO FAR !!!!
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

### Region or state getter for IP address of user
def getLocation(ip):                    
    response = requests.get("http://ip-api.com/json/{}?fields=regionName".format(ip))
    js = response.json()
    return js


#################################### HOME PAGE ###########################################
@pages.route('/', methods=['POST','GET'])                       
def homepage():
    ### Replace IP with request IP getter on deployment ###
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) 
    print(ip)
    
    location = getLocation(ip) # Returns a dictionary of location details
    region = location.get('regionName')
    print(region)
    
    # When search is posted
    if request.method == 'POST':  
        postedSearch = request.form.get('search')      
        return redirect(url_for('pages.results', search=postedSearch, region=region))
    
    return render_template('homepage.html')
#########################################################################################################################################################



#################################### RESULTS PAGE #########################################
@pages.route('/results', methods=['POST','GET'])                    
def results():
    search = request.args.get('search')
    region = request.args.get('region')
    print(region)
    tz = timezone('EST')
    
    searchLimit = 5         # For how many cars to be returned by pycraigslist
    
    howOld = 10          # For how old the car must be in the database to be shown
    
    ### POST
    if request.method == 'POST':
        favCar = db.session.query(Car).filter(Car.carID==request.form.get('favButton')).first()       # Button submits the car id of the car tab
        fillFavCar = db.session.query(Car).filter(Car.carID==request.form.get('fillFavButton')).first()
        curUser = db.session.query(User).filter(User.userEmail==session['email']).first()       # Current user is accessed through the email of the session
        
        if request.form.get('favButton') != None:             # To check if the favorite button was clicked
            curUser.favs.append(favCar)               # Add the car to the favorited cars for the user
            db.session.commit()
            
        if request.form.get('fillFavButton') != None:
            curUser.favs.remove(fillFavCar)
            db.session.commit()
            
        if request.form.get('search') != None:
            postedSearch = request.form.get('search')      
            return redirect(url_for('pages.results', 
                                    search=postedSearch, 
                                    region=region, 
                                    has_image=request.form.get('filterImg'), 
                                    posted_today=request.form.get('filterToday'), 
                                    search_distance=request.form.get('filterDist'), 
                                    zip_code=request.form.get('filterZip'), 
                                    min_price=request.form.get('filterMinPrice'), 
                                    max_price= request.form.get('filterMaxPrice'), 
                                    min_year=request.form.get('filterMinYear'),
                                    max_year=request.form.get('filterMaxYear'),
                                    min_miles=request.form.get('filterMinMiles'),
                                    max_miles=request.form.get('filterMaxMiles'),
                                    min_engine_displacement=request.form.get('filterMinEng'),
                                    max_engine_displacement=request.form.get('filterMaxEng'),
                                    condition=request.form.get('filterConditionList').value, 
                                    auto_cylinders=request.form.get('filterCylindersList').value, 
                                    auto_drivetrain=request.form.get('filterDriveList').value, 
                                    auto_fuel_type=request.form.get('filterFuelList').value, 
                                    auto_paint=request.form.get('filterPaintList').value, 
                                    auto_size=request.form.get('filterSizeList').value, 
                                    auto_title_status=request.form.get('filterTitleList').value, 
                                    auto_transmission=request.form.get('filterTransList').value, 
                                    auto_bodytype=request.form.get('filterBodyList').value, 
                                    language=request.form.get('filterLangList').value))

    ### GET for when result page is prompted 
    elif request.method == 'GET':
        for city in stateMap.get(region):
            results = pycraigslist.forsale.cta(site=city, query=search)
            
            ### Search through all the resulting cars that are given by the API ###
            for car in results.search(limit=searchLimit):       # Search limit applied here
                carTitle = car['title']         # Current car title
                carInDB = db.session.query(Car).filter(Car.carTitle==carTitle).first()     # Check car in DB, is None type if not in DB
                
                ### ADD CAR TO DB FILTER ###
                if carInDB == None and car.get('price') >= '$100' and search.lower() in carTitle.lower():       # Car title cannot already be in DB, price cannot be zero, car model must be in title
                ############################

                    ### BeautifulSoup implementation for image scraper ###
                    soup = BeautifulSoup(requests.get(car.get('url')).text, 'html.parser')
                    allImgs = soup.find('img')
                    
                    ### MUST HAVE IMAGE FOR THE CAR FOUND ###
                    if allImgs is not None:     
                        dateFormat = datetime.strptime(car.get('last_updated'), '%Y-%m-%d %H:%M') # Format of the datetime given by the API to DateTime
                        
                        # Creating the car object
                        curCar = Car(carCountry='US', carRegion=region, carArea=car.get('area'), carImage=allImgs['src'], carTitle=carTitle, carPrice=car.get('price'), carLink=car.get('url'), carDatePosted=dateFormat)
                        
                        db.session.add(curCar)
                        db.session.commit()
    
    ### ALL CARS IN DATABASE THAT IS VALID TO BE SHOWN ON THE WEBSITE ###
    validCars = db.session.query(Car).filter(Car.carDatePosted >= datetime.now(tz)-timedelta(days=howOld), Car.carTitle.contains(search), Car.carPrice!='$0').all()
    
    return render_template('results.html', search=search, region=region, Result=validCars, user=db.session.query(User).filter(User.userEmail==session['email']).first())
##################################################################################################################################################################################################################################################################################################################




#################################### ABOUT US PAGE ( ADD SOCIALS ETC ) #############################################################################
@pages.route('/aboutus', methods=['GET'])                           
def aboutus():
    return render_template('aboutus.html')
###################################################################################################################################################




##################################### PROFILE PAGE OF CURRENT USER ( ONLY ACCESSIBLE IF SIGNED IN ) #################################################
@pages.route('/profile', methods=['POST','GET'])                
@login_required
def profile():
    if request.method == 'POST':
        print(request.form.get('fillFavButton'))
        fillFavCar = db.session.query(Car).filter(Car.carID==request.form.get('fillFavButton')).first()
        curUser = db.session.query(User).filter(User.userEmail==session['email']).first()       # Current user is accessed through the email of the session
        
        if request.form.get('fillFavButton') != None:
            curUser.favs.remove(fillFavCar)
            db.session.commit()
        
    return render_template('profile.html', user=db.session.query(User).filter(User.userEmail==session['email']).first())
###################################################################################################################################################




##################################### REGISTER PAGE ################################################################################################
@pages.route('/register', methods=['POST','GET'])                           
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('pw')
        confpassword = request.form.get('confpw')
        
        userCheck = User.query.filter_by(userEmail=email).first()            ### Check if user already in DB
        userNameCheck = User.query.filter_by(userUsername=username).first()
        
        if userCheck:
            flash('Email already exists.', category='ERROR')
        elif userNameCheck:
            flash('Username already exists.', cateogry='ERROR')
        elif len(email) < 4:
            flash('Invalid Email: Email must be greater than 4 characters.', category='ERROR')
        elif len(password) < 6:
            flash('Invalid Password: Password must be at least 6 or more characters.', category='ERROR')
        elif password != confpassword:
            flash('Invalid Confirmation: Passwords do not match.', category='ERROR')
        else:
            newUser = User(userUsername=username, userEmail=email, userPassword=generate_password_hash(password, method='sha256'))         ### Hash for the password
            
            db.session.add(newUser)
            db.session.commit()
            
            # Login the user to the website
            login_user(newUser)
            
            # Add the email of the user to the current session
            session['email']=email
            
            flash('Account created!', category='SUCCESS')
            return redirect(url_for('pages.homepage'))
    return render_template('register.html')
###################################################################################################################################################




##################################### LOGIN PAGE ################################################################################################
@pages.route('/login', methods=['POST','GET'])                     
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pw')
        
        user = User.query.filter_by(userEmail=email).first()        # Find the user with the email that was given
        
        if user:
            if check_password_hash(user.userPassword, password):            # Check the password
                flash('Logged in successfully!', category='SUCCESS')
                login_user(user)
                session['email']=email
                return redirect(url_for('pages.homepage'))
            else:
                flash('Incorrect Password', category='ERROR')
        else:
            flash('No user with that email', category='ERROR')
    return render_template('login.html')
###################################################################################################################################################



##################################### LOGOUT PAGE ################################################################################################
@pages.route('/logout', methods=['GET'])                       
def logout():           
    if not current_user.is_authenticated:
        flash('You are not logged in', category='message')
    else:
        logout_user()
        flash('Successfully Logged Out!', category='SUCCESS')
    return redirect(url_for('pages.homepage'))
###################################################################################################################################################