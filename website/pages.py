from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
import json
from .models import Result

import requests

from craigslist import CraigslistForSale                #CTA for cars and trucks
import pycraigslist

pages = Blueprint('pages', __name__)    

def getLocation(ip):
    response = requests.get("http://ip-api.com/json/{}".format(ip))
    js = response.json()
    return js

@pages.route('/', methods=['POST','GET'])
def homepage():
    if request.method == 'POST': 
        postedSearch = request.form.get('search')      
        
        ip = request.remote_addr
        location = getLocation(ip)
        
        print(ip + "lol")
        
        country = location.get("country")
        city = location.get("city")
        
        
        
        postedSite = request.form.get('site')  
        postedArea = request.form.get('area')
        return redirect(url_for('pages.results', search=postedSearch, site=postedSite, area=postedArea))
                    
    return render_template('homepage.html')

@pages.route('/results', methods=['POST','GET'])
def results():
    postedSearch = request.args.get('search', None)
    postedSite = request.args.get('site', None)
    postedArea = request.args.get('area', None)
    
    searched = False
    if postedSearch != '':
        searched = True
        if postedSite == "":
            if postedArea == "":
                cars = pycraigslist.forsale.cta(site='sfbay', query=postedSearch)
            else:
                cars = pycraigslist.forsale.cta(site='sfbay', area=postedArea, query=postedSearch)
        elif postedArea == '':
            cars = CraigslistForSale(site=postedSite, category='cta')
        else:
            cars = pycraigslist.forsale.cta(site=postedSite, area=postedArea, query=postedSearch)
    elif postedArea == '':
        cars = CraigslistForSale(site=postedSite, category='cta')
    else:
        cars = CraigslistForSale(site=postedSite, area=postedArea, category='cta')
    
    newResult = Result()
    newResult.results.clear()
    if searched:
        for car in cars.search(limit=5):
            newResult.results.append(car)
    else:
        for car in cars.get_results(sort_by='newest', limit=5):
            newResult.results.append(car)
    
    return render_template('results.html', Result=newResult)
                    
        
