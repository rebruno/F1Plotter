import unittest
from src.f1plotter.APIrequests import *



class TestRequests(unittest.TestCase):

    def test_raceresult(self):
        req = APIRequester()
        req.race(2023, 14)
        results = req.get_results()

        self.assertTrue(results[0]["max_verstappen"]["position"] == 1)

    def test_racename(self):
        req = APIRequester()
        name = req.get_racename(2023, 14)

        self.assertEqual(name, "Italian Grand Prix")
        
    def test_laps(self):
        req = APIRequester()
        laps = req.race(2023, 14).get_laps()[0]

        self.assertEqual(len(laps["max_verstappen"]), 51)
        self.assertEqual(len(laps["ocon"]), 39)

    def test_get_specific_driver_information(self):
        req = APIRequester()
        req.race(2023, 14)
        req.driver("max_verstappen")
        req.lap(30) #lap 30

        laps = req.get_laps()
        laps = req.get_laps()
        print(laps)

