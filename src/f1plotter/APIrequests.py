import json
import requests as req
import requests_cache as cache
import numpy as np
import re

from .methods import *

#requests_cache, used for caching requests. Will be replaced later but it works for now
cache.install_cache()


class APIRequester:

	"""

	Request URLs are of the form
	http[s]://ergast.com/api/<series>/<season>/<round>/...

	which can then be followed with
		-Season List

	"""

	def __init__(self):
		self.raceNames = None
		self.reqJSON = None

		self.reset_params()

	def get_request(self, url):
		"""
		Tries to load JSON content. 
		If the limit is less than the total, then a 2nd request is done to get all the data to avoid further calls
		"""
		getRequest = req.get(url)
		getRequest.raise_for_status() #If a 400+ code is returned, an error is raised

		getJSON = json.loads(getRequest.content)

		if int(getJSON["MRData"]["limit"]) < int(getJSON["MRData"]["total"]): #Runs a 2nd request if there is more data
			self.params["limits"]["limit"] = int(getJSON["MRData"]["total"])
			return self.run_request()

		return getJSON

	def reset_variables(self):
		"""
		Used to reset variables, should call it in between every seperate use
		Call automatically everytime get_STATISTIC() is called
		"""
		self.raceNames = None
		self.reqJSON = None

	def reset_params(self):
		self.crtieria = None
		self.params = {
			"race": {
				"season":		None,
				"round":		None,
			},
			"qualifiers": {
				"drivers":		None,
				"constructor":	None,
				"grid":			None,
				"qualifying":	None,
				"sprint":		None,
				"result":		None,
				"status":		None,
				"standing":		None,
				"races":		None,
				"pit_stop":		None,
				"laps":			None,
			},
			"limits":{
				"limit":		None,
				"offset":		None,
			}			
		}

	def race(self, season, roundN=None):
		"""
		Can either specify a season(don't pass an argument for roundN) or a specific race from a season.
		This must be set before using methods like get_laps(), get_drivers(), etc... that depend on a specific race.
		Both are integers, and must be valid(season is a year, roundN must be one of the rounds for a season)
		A simple way to find out the (season, roundN) needed is to check the Wikipedia article for a given season.

		"""
		self.params["race"]["season"] = season
		self.params["race"]["round"] = roundN
		return self

	def driver(self, driverID):
		"""
		driverID is a driverID used by the Ergast API to uniquely identify drivers.
		Generally this is the lowercase of their family name, but in the case of drivers that share their family name
		(e.g. Michael and Ralf Schumacher), their first name is prepended. 

		TODO: search_driver(givenName, familyName) can also be used to find the driverID, which will return a list of driverIDs
		that fit the given and family name.
		"""
		self.params["qualifiers"]["drivers"] = driverID
		return self

	def lap(self, lapN):
		self.params["qualifiers"]["laps"] = lapN
		return self

	def get_laps(self):
		"""
		Returns a dictionary in the format of {driverid:[laptime1, laptime2, ..., ]}
		where driverid is a valid driverid and laptimeX is the laptime for lap X in seconds. 
		"""
		self.reset_variables()

		self.criteria = "laps"
		
		self.params["limits"]["limit"] = 87 #

		self.reqJSON = self.run_request()

		if len(self.reqJSON["MRData"]["RaceTable"]["Races"]) == 0:
			print("Error in getting laps.")
			return np.array([])


		lapTimeData = {}
		raceNames = []

		for raceN,race in enumerate(self.reqJSON["MRData"]["RaceTable"]["Races"]):
			print("here", raceN)
			raceLaps = {}
			for driver in race["Laps"][0]["Timings"]:
				raceLaps[driver["driverId"]] = []

			for lap in race["Laps"]:
				for driver in lap["Timings"]:
					raceLaps[driver["driverId"]].append(get_sec(driver["time"]))
				#raceLaps = np.array([get_sec(lap["Timings"][0]["time"]) for lap in race["Laps"]])

			#Index of race is same index in raceNames
			lapTimeData[raceN] = raceLaps
			raceNames.append(race["raceName"]) 

		self.raceNames = raceNames

		self.reset_params()
		return lapTimeData

	def get_drivers(self):
		"""
		Must set the race parameter first( APIRequester.race(season, roundNumber))

		Returns a dictionary in the format of 
		{'michael_schumacher': 
			{	'driverId': 'michael_schumacher', 
				'code': 'MSC', 
				'url': 'http://en.wikipedia.org/wiki/Michael_Schumacher', 
				'givenName': 'Michael', 
				'familyName': 'Schumacher', 
				'dateOfBirth': '1969-01-03', 
				'nationality': 'German'
			}
		}
		"""
		self.reset_variables()

		self.criteria = "drivers"
		self.params["limits"]["limit"] = 34 #

		self.reqJSON = self.run_request()

		driverData = {}

		for driverN, driver in enumerate(self.reqJSON["MRData"]["DriverTable"]["Drivers"]):
			driverID = driver["driverId"]
			driverData[driverID] = driver

		self.reset_params()
		return driverData



	def run_request(self):
		reqURL = self.create_url(self.params, self.criteria)
		print("ReqURL is {}".format(reqURL))
		return self.get_request(reqURL)

	def create_url(self, params, criteria):
		"""
		Possible URLs
		Races: base + season number .json
		Drivers: base + {season} + drivers .json
		
		Laps is season + round_number + {drivers/driverID} + laps + {lap_number}
		'https://ergast.com/api/f1/2011/5/drivers/alonso/laps/1'

		In general, if a season is specified, it goes first
		If a round number is specificed, it goes next(only if a season is specified)
		Driver goes before any other refinments but it is optional

		To build URL, need season/round usually, then some filters(which driver, constructor, etc...
		)


		params is a dictionary
		For example, if the above URL is wanted, you would pass
		{"season":2011, "round":5, "drivers":"alonso", "laps":1}
		with criteria = "laps"
		This would be generated by calling get_lap_param(season, round, driver, lap)
		Criteria = "lap"
		"""
		#Laps
		reqURL = URLBuilder()
		param_keys = params.keys()

		qualifiers = params["qualifiers"]

		if criteria == None:
			raise Exception("Criteria must be defined")
		if params["race"]["season"] != None:
			reqURL.append(params["race"]["season"])
			if params["race"]["round"] != None: 
				#Only add the round IF season is defined. This would otherwise be an error
				reqURL.append(params["race"]["round"])

		for k,v in qualifiers.items():
			if v != None and k != criteria:
				reqURL.append(v, k)

		reqURL.append(qualifiers[criteria], criteria)
		reqURL.json()
		reqURL.limit(params["limits"])

		return reqURL.baseURL

		
		


class URLBuilder:
	baseURL = "https://ergast.com/api/f1" 

	def __init__(self):
		pass

	def reset(self):
		self.baseURL = "https://ergast.com/api/f1/" 

	def append(self, path, key = None):
		if key == None:
			self.baseURL += "/" + str(path)
		elif path == None:
			self.baseURL += "/{}".format(key)
		else:
			self.baseURL += "/" + str(key) + "/" + str(path)

	def json(self):
		self.baseURL += ".json"
	
	def limit(self, limitParams):
		if limitParams["limit"] != None:
			self.baseURL += f"?limit={limitParams['limit']}"
		if limitParams["offset"] != None:
			self.baseURL += f"?limit={limitParams['offset']}"