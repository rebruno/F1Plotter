from .query import *
from .methods import *

import numpy as np


def lap_comparison(raceID, driverIDList, n = 25, percent = 1, startLap = 0, endLap = None):
    """
    Takes a list of driverIDs and a raceID.
    Compares the lap averages(up to n fastest laps) between drivers.
    
    Takes gaps to the first driver in the driverIDList
    """

    if len(driverIDList) == 0:
        return {}

    driverLaps = ErgastQuery().get_laps(raceID, driverIDList)
    if len(driverLaps) == 0:
        return {}

    driverGaps = {driverIDList[0]:0}

    if len(driverLaps[driverIDList[0]]["laptime"]) == 0:
        return {}

    firstDriverAvg = np.average(sorted(driverLaps[driverIDList[0]]["laptime"])[:n])
    for driverID in driverIDList[1:]:
        if len(driverLaps[driverID]["laptime"]) == 0:
            driverGaps[driverID] = None
            continue
                
        driverGaps[driverID] = np.average(sorted(driverLaps[driverID]["laptime"])[:n]) - firstDriverAvg

    return driverGaps

def team_lap_comparison(raceID, teamIDList, n=25, percent=1, startLap = 0, endLap = None):
    """
    Same as lap_comparison but between teammates
    """
    teamGaps = {}
    for team in teamIDList:
        driverGaps = lap_comparison(raceID, teamIDList[team], n, percent, startLap, endLap)
        teamGaps[team] = driverGaps

    return teamGaps
