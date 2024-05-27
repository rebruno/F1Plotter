# F1Plotter
* Python module to access F1 race results, lap times, team and driver information
* Functions to visualize data using Matplotlib

## Installation: 
Run the following in the same directory as ```pyproject.toml```.
``` 
python -m build
pip install --find-links install dist/f1plotter-0.0.1-py3-none-any.whl
``` 
The library can then be used through ```import f1plotter```.

## Testing
Tests are in the ```tests``` folder. Compatible with Python's unittest framework and pytest.
```pytest tests```

## Classes
### APIRequester
Currently supports getting race names, results, driver, qualifying and lap information.<br>
Any call must have the race specified. An example of using follows, where get_laps() can also be any other _get_ function.<br>
``` 
from f1plotter.query import ErgastQuery

query = ErgastQuery()
driver_list = query.get_drivers(2023)
teams_list = query.get_teams((2023, 1))
```

### Plotter
Uses a query class and displays it using Matplotlib.<br>
Currently, only head_to_head_laptime() is supported. 

``` 
from matplotlib import pyplot as plt
from f1plotter.plotter import Plotter
from f1plotter.query import ErgastQuery

plotter = Plotter(ErgastQuery())
driverIDList = ["max_verstappen", "leclerc", "perez"]
season = 2023
race = 1
fig, axe = plotter.head_to_head_laptime(
					raceID = (season, race), 
					driverIDList = driverIDList, 
					startLap = 0, endLap = None)
plt.show()


plotter = Plotter(DataFormatter())
driverIDList = ["max_verstappen", "leclerc", "perez"]
season = 2023
race = 1
fig, axe = plotter.head_to_head_laptime(raceID = (season, race), 
					driverIDList = driverIDList, 
					startLap = 0, endLap = None)
plt.show()

```
