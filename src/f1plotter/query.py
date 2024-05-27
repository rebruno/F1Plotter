from .APIrequests import APIRequester
import numpy as np

class ErgastQuery:

    def __init__(self, debug = False):
        self.debug = debug
        self.requester = APIRequester(debug)

    def get_racename(self, raceID):
        """
        raceID is a pair (season, round_number)
        """
        return self.requester.get_racename(*raceID[0:2])

    def get_laps(self, season, round_number, driverIDList, convertNumpy = False, startLap = 0, endLap = None):
        """
        raceID is a pair (season, round_number), where season is a year and round_number is a 1-indexed number
        ex: The 2023 Bahrain F1 race would be raceID = (2023, 1)

        driverIDList is a list of driver IDs used by Ergast

        Returns a dictionary, driverLaps
        The format of this dictionary is
        { driverID1: 
            {
                "laptime":[],
                "lap":[]
            }
        }
        "lap" contains the lap number it happened on (e.g. 5) and "laptime" contains the seconds it took(for the lap at that index)
        """
        self.requester.race(season, round_number)
        driverLaps = {}

        requestedLaps = self.requester.get_laps()[0]

        for driver in driverIDList:
            driverLaps[driver] = {}
            
            if driver not in requestedLaps:
                if self.debug:
                    print(f"Driver {driver} missing in request laps")
                driverLaps[driver]["laptime"] = np.array([])    
                driverLaps[driver]["lap"] = np.array([])    
                continue
                
            driverLaps[driver]["laptime"] = requestedLaps[driver][startLap:endLap]
            driverLaps[driver]["lap"] = np.arange(1+startLap, len(driverLaps[driver]["laptime"])+startLap+1)
            
            if convertNumpy:
                driverLaps[driver]["laptime"] = np.array(driverLaps[driver])

        return driverLaps

    def get_drivers(self, season, round_number = None):
        """
        If season and round_number are None, then this gets every driver that has ever raced in F1(that is in the database)
        Returns a list of driverIDs
        """
        self.requester.race(season, round_number)
        drivers = self.requester.get_drivers()
        return list(drivers.keys())

    def get_teams(self, season, round_number = None):
        self.requester.race(season, round_number)
        resultData = self.requester.get_results()[0]

        teams = {}

        for driver in resultData:
            if resultData[driver]["Constructor"] not in teams:
                teams[resultData[driver]["Constructor"]] = [driver]
            else:
                teams[resultData[driver]["Constructor"]].append(driver)

        return teams

