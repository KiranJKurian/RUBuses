#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import json
import urllib
import jinja2
import webapp2
import os
from google.appengine.api import urlfetch

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

url="https://nstanlee.rutgers.edu/~rfranknj/mobile/1/places.txt"
result = urlfetch.fetch(url)
places = json.loads(result.content)

String=""

def nearbyFunc(lat,lon):
	url2="http://runextbus.herokuapp.com/nearby/"+lat+"/"+lon
	result2 = urlfetch.fetch(url2)
	nearby = json.loads(result2.content)
	return nearby

def route(bus,nearby):
	for stop in bus:
		for stop2 in nearby:
			if stop['title']==stop2:
				global String
				String+="&nbsp;&nbsp;&nbsp;&nbsp;"+stop['title']+"<br>"
				if stop["predictions"]:
					for prediction in stop["predictions"]:
						String+="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Incoming: "+prediction['minutes']+" minutes "+str(int(prediction['seconds'])%60)+" seconds"+"<br>"

class MainHandler(webapp2.RequestHandler):
    def get(self):
    	template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render())
        
class magic(webapp2.RequestHandler):
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render())
        building=(self.request.get('location')).lower()
        if building=='rsc' or building=="casc" or building=='rcs' or building=='cacc' or building=='college ave student center' or building=='college ave campus center':
			building='rutgers student center'
        elif building=='bsc'or building=='bcc' or building=='busch student center':
			building='busch campus center'
        elif building=='lsc' or building=='lcs' or building=='livingston campus center':
			building='livingston student center'
        elif building=='hill' or building=='hill center':
			building='Hill Center Bldg for the Mathematical Sciences'.lower()
        buildingErrorCheck=True
        for location in places['all']:
			if (places['all'][location]['title']).lower()==building:
				lat= places['all'][location]['location']['latitude']
				lon=places['all'][location]['location']['longitude']
				buildingErrorCheck=False
        if buildingErrorCheck:
			self.response.write("<center>Couldn't find building, <a href='/'>try again</a></center>")
			return
        nearby=nearbyFunc(lat,lon)
        url3="http://runextbus.heroku.com/locations"
        result3 = urlfetch.fetch(url3)
        locations = json.loads(result3.content)
        global String
        for bus in locations:
			String+=bus+"<br>"
			url4="http://runextbus.heroku.com/route/%s"%bus
			result4 = urlfetch.fetch(url4)
			routeStuff = json.loads(result4.content)
			route(routeStuff,nearby)
        self.response.write("%s"%String)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/magic', magic)
], debug=True)
