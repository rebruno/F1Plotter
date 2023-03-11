import json
import requests as req
import requests_cache as cache

import re

from .methods import *

#requests_cache, used for caching requests. Will be replaced later but it works for now
cache.install_cache()

driver_limit = 857

class APIRequester:

	"""

	Request URLs are of the form
	http[s]://ergast.com/api/<series>/<season>/<round>/...

	which can then be followed with
		-Season List

	"""

	def __init__(self):
		self.lastURLRequest = None #Kind of used as a caching. Since the results are cached, accessing this is pretty fast and useful for stuff like getting the racename

		self.reset_params()

	def get_request(self, url : str):
		"""
		Tries to load JSON content. 
		If the limit is less than the total, then a 2nd request is done to get all the data to avoid further calls
		"""
		self.lastURLRequest = url

		getRequest = req.get(url)
		getRequest.raise_for_status() #If a 400+ code is returned, an error is raised

		getJSON = json.loads(getRequest.content)

		if int(getJSON["MRData"]["limit"]) < int(getJSON["MRData"]["total"]): #Runs a 2nd request if there is more data
			self.params["limits"]["limit"] = int(getJSON["MRData"]["total"])
			return self.run_request()



		return getJSON

	def reset_params(self):
		self.criteria = None
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

		"""
		self.params["qualifiers"]["drivers"] = driverID
		return self

	def lap(self, lapN):
		self.params["qualifiers"]["laps"] = lapN
		return self

	def limit(self, L):
		self.params["limits"]["limit"] = L


	def get_racename(self, season, round_number):
		#Check if last request matches (season,round_number) since it is likely that the last request
		#Was for the same race
		reqJSON = self.get_request(self.lastURLRequest)["MRData"]["RaceTable"]
		if int(reqJSON["season"]) == season:
			for race in reqJSON["Races"]:
				if int(race["round"]) == round_number:
					return race["raceName"]

		#Else, run a request for it. 

		self.criteria = "results"
		self.race(season, round_number)

		reqJSON = self.run_request()

		if len(reqJSON["MRData"]["RaceTable"]["Races"]) == 0:
			print("Error in getting race name.")
			return ""
		
		return reqJSON["MRData"]["RaceTable"]["Races"][0]["raceName"]



	def get_laps(self):
		"""
		Returns a dictionary in the format of {driverid:[laptime1, laptime2, ..., ]}
		where driverid is a valid driverid and laptimeX is the laptime for lap X in seconds. 
		"""

		self.criteria = "laps"
		
		if self.params["limits"]["limit"] == None:
			self.limit(87) #

		reqJSON = self.run_request()

		if len(reqJSON["MRData"]["RaceTable"]["Races"]) == 0:
			print("Error in getting laps.")
			return []


		lapTimeData = {}

		for raceN,race in enumerate(reqJSON["MRData"]["RaceTable"]["Races"]):
			raceLaps = {}
			for driver in race["Laps"][0]["Timings"]:
				raceLaps[driver["driverId"]] = []

			for lap in race["Laps"]:
				for driver in lap["Timings"]:
					raceLaps[driver["driverId"]].append(get_sec(driver["time"]))

			lapTimeData[raceN] = raceLaps

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

		self.criteria = "drivers"
		if self.params["limits"]["limit"] == None:
			self.limit(34) #

		reqJSON = self.run_request()

		driverData = {}
		for driverN, driver in enumerate(reqJSON["MRData"]["DriverTable"]["Drivers"]):
			driverID = driver["driverId"]
			driverData[driverID] = driver

		self.reset_params()
		return driverData

	def get_qualifying(self):
		"""
		Returns qualifying results, in the format of {'driverId': {'Q1' : time}}
		Results are not full for years before 2003, but an alternative will be added in the future. 

		"""

		self.criteria = "qualifying"

		if self.params["limits"]["limit"] == None:
			self.limit(20)

		reqJSON = self.run_request()

		qualifyingData = {}

		for qualiN, quali in enumerate(reqJSON["MRData"]["RaceTable"]["Races"]):
			qualifyingTimes = {}

			for driver in quali["QualifyingResults"]:
				qualifyingTimes[driver["Driver"]["driverId"]] = {}
				for qSession in ["Q1", "Q2", "Q3"]:
	
					if qSession in driver:
						qualifyingTimes[driver["Driver"]["driverId"]][qSession] = get_sec(driver[qSession])
		
			qualifyingData[qualiN] = qualifyingTimes


		self.reset_params()
		return qualifyingData

	def search_id(self, name):
		"""
		regex search of all drivers.
		This should be cached and since all drivers are cached, any successive calls don't need to make any requests to Ergast 
		Searches all drivers to find the corresponding driver ID based on their name. For example, passing in "Schumacher" will return Michael, Ralf, and Mick Schumacher and their id's 
		as a dictionary {'driverId':'givenName familyName'}.
		"""
		self.reset_variables()

		self.limit(driver_limit)
		drivers = self.get_drivers()

		driverStrings = ["{} {} {}".format(driver["driverId"], driver["givenName"], driver["familyName"]) for driver in drivers.values()]
		possibleMatches = [idName for idName, match in [(searchString.split(" ", 1), re.search(name, searchString, re.IGNORECASE)) for searchString in driverStrings] if match is not None ]
		

		self.reset_params()
		return dict(possibleMatches)

	def run_request(self):
		reqURL = self.create_url(self.params, self.criteria)
		print("Request URL is {}".format(reqURL))
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



