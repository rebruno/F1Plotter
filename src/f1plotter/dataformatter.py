from .APIrequests import APIRequester
import numpy as np

"""

This is the class to format the data for the plotter class
Simply rewrite this class and it should work with the plotter class
In this case, I am using it with APIRequester()
There is also another project on my github which uses it with an sqlite3 database

This should have(for the time being):
-get_laps(), returning {driver: [laptimes]} and {driver: [lapNumber]}
	lapNumber is the lap number for a lap time. i.e. [36, 34, 35], [3,4,5] would be laptimes for laps 3, 4, and 5


"""
class DataFormatter:

	def __init__(self):
		self.requester = APIRequester()
		self.lastRequestJSON = None
		self.raceNames = None

	def get_laps(self, raceID, driverIDList, convertNumpy = False, startLap = 0, endLap = None):
		"""
		raceID is a pair (season, round_number), where season is a year and round_number is a 1-indexed number
		ex: The 2023 Bahrain F1 race would be raceID = (2023, 1)

		driverIDList is a list of driver IDs used by Ergast

		Returns a dictionary of {driverID:[laptimes]} along with another dictionary containg X values for the laps.
		This is useful mostly for other racing series where driver switches happen
		"""
		season, round_number = raceID
		self.lastRequestJSON = None


		self.requester.race(season, round_number)
		driverLaps = {}
		driverX = {}

		#Build lapTimeData from list of all drivers
		#This means calling without the driverID and filtering the results
		requestedLaps = self.requester.get_laps()[0] #Only 1 race is requested so only first index is used


		for driver in driverIDList:
			driverLaps[driver] = requestedLaps[driver][startLap:endLap]
			driverX[driver] = np.arange(1+startLap, len(driverLaps[driver])+startLap+1)

			if convertNumpy:
				driverLaps[driver] = np.array(driverLaps[driver])


		self.lastRequestJSON = self.requester.reqJSON
		self.raceNames = self.requester.raceNames

		#plotRequester.reset_variables()

		return driverLaps, driverX

	def get_drivers(self, season = None, round_number = None):
		"""
		If season and round_number are None, then this gets every driver that has ever raced in F1(that is in the database)
		"""

		self.lastRequestJSON = None
		self.requester.race(season, round_number)
		self.lastRequestJSON = self.requester.reqJSON
		