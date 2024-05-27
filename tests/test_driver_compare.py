import unittest
from src.f1plotter.driver_compare import *

class TestComparison(unittest.TestCase):

    def test_lap_compare(self):

        #{'max_verstappen': 0, 'perez': 0.1672399999999925, 'leclerc': 0.23403999999999314, 'sainz': 0.22975999999999885}
        driverIDList = ["max_verstappen", "perez", "leclerc", "sainz"]
        raceID = (2023, 14)


        gaps = lap_comparison(*raceID, driverIDList)

        self.assertEqual(gaps[driverIDList[0]], 0)

        assert gaps[driverIDList[0]] == 0 

    def test_team_gap(self):
        #{'red_bull': {'max_verstappen': 0, 'perez': 0.1672399999999925}, ...}
        raceID = (2023, 14)
        team_gaps = team_lap_comparison(*raceID, ErgastQuery().get_teams(*raceID))

        redbull_gap = team_gaps['red_bull']

        self.assertEqual(redbull_gap["max_verstappen"], 0)
        self.assertTrue(redbull_gap["perez"] > 0)
        
        assert redbull_gap["max_verstappen"] == 0
        assert redbull_gap["perez"] > 0


if __name__ == "__main__":
    unittest.main()