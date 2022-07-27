from re import L
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from .__init__ import POSSTACKKEY
import json
from .models import Result
import requests
import http.client, urllib.parse

from craigslist import CraigslistForSale                #CTA for cars and trucks
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

# def posStack(lat, lon):                                                                       DON'T NEED THIS METHOD FOR NOW
#     positionStackConnection = http.client.HTTPConnection('api.positionstack.com')

#     pos = str(lat) + "," + str(lon)
    
#     params = urllib.parse.urlencode({
#         'access_key': '52382ded2394b8158b1ae36a14adb9d7',
#         'query': pos,
#         'limit': 1,
#     })

#     positionStackConnection.request('GET', '/v1/reverse?{}'.format(params))

#     res = positionStackConnection.getresponse()
#     data = res.read()
#     return data.decode('utf-8')

def getLocation(ip):
    response = requests.get("http://ip-api.com/json/{}?fields=regionName".format(ip))
    js = response.json()
    return js

@pages.route('/', methods=['POST','GET'])
def homepage():
    if request.method == 'POST': 
        postedSearch = request.form.get('search')      
        postedSite = request.form.get('site')  
        postedArea = request.form.get('area')
        return redirect(url_for('pages.results', search=postedSearch, site=postedSite, area=postedArea))
    elif request.method == 'GET':
        ip = "207.228.238.7"        #24.48.0.1
        location = getLocation(ip)

        regionOrState = location.get('regionName')
    return render_template('homepage.html')

@pages.route('/results', methods=['POST','GET'])
def results():
    ip = "192.199.248.75"        #24.48.0.1
    location = getLocation(ip)

    region = location.get('regionName')
    
    postedSearch = request.args.get('search', None)
    # postedSite = request.args.get('site', None)
    # postedArea = request.args.get('area', None)
    
    newResult = Result()
    newResult.results.clear()

    if postedSearch != '':
        for state in stateMap.get(region):
            cars = pycraigslist.forsale.cta(site=stateMap.get(region)[0], query=postedSearch)
            for car in cars.search(limit=10):
                newResult.results.append(car)
    else:
        for state in stateMap.get(region):
            cars = CraigslistForSale(site=stateMap.get(region)[0], category='cta')
            for car in cars.get_results(sort_by='newest', limit=10):
                newResult.results.append(car)
    
    # if postedSearch != '':
    #     searched = True
    #     if postedSite == "":
    #         if postedArea == "":
    #             cars = pycraigslist.forsale.cta(site='sfbay', query=postedSearch)
    #         else:
    #             cars = pycraigslist.forsale.cta(site='sfbay', area=postedArea, query=postedSearch)
    #     elif postedArea == '':
    #         cars = CraigslistForSale(site=postedSite, category='cta')
    #     else:
    #         cars = pycraigslist.forsale.cta(site=postedSite, area=postedArea, query=postedSearch)
    # elif postedArea == '':
    #     cars = CraigslistForSale(site=postedSite, category='cta')
    # else:
    #     cars = CraigslistForSale(site=postedSite, area=postedArea, category='cta')
    return render_template('results.html', Result=newResult)
                    
        
