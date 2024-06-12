# F1Plotter
* Python module to access F1 race results, lap times, team and driver information
* Functions to visualize data using Matplotlib, returning a figure and axe for customization.

## Installation: 
Run the following in the same directory as ```pyproject.toml```.
``` 
python -m build
pip install --find-links install dist/f1plotter-0.0.1-py3-none-any.whl
``` 
The library can then be used through ```import f1plotter```.


## Classes
### APIRequester
Currently supports getting race names, results, driver, qualifying and lap information.<br>
Any call must have the race specified by season and race number.<br>
Check [APIrequests.py](/src/f1plotter/APIrequests.py) for all available functions.
``` 
from f1plotter.query import ErgastQuery

query = ErgastQuery()
driver_list = query.get_drivers(2023)
teams_list = query.get_teams((2023, 1))
```

### Plotter
Uses a query class and displays it using Matplotlib.<br>
Currently, head_to_head_laptime() and boxplot() are available.
- head_to_head_laptime()
``` 
from matplotlib import pyplot as plt
from f1plotter.plotter import Plotter
from f1plotter.query import ErgastQuery

plotter = Plotter(ErgastQuery())
driverIDList = ["max_verstappen", "leclerc", "russell", "norris"]

season = 2024
race = 9
fig, axe = plotter.head_to_head_laptime(
		raceID = (season, race), 
		driverIDList = driverIDList, 
		startLap = 0, endLap = None)
plt.show()
```
![Example of plotting laptimes for the 2024 Canadian Grand Prix](https://github.com/rebruno/F1Plotter/assets/101484447/5d1d537d-c3fb-465e-9c2b-6a3347e4134a)

- boxplot()
``` 
from matplotlib import pyplot as plt
from f1plotter.plotter import Plotter
from f1plotter.query import ErgastQuery

plotter = Plotter(ErgastQuery())
driverIDList = ["max_verstappen", "leclerc", "norris", "russell"]
season = 2024
race = 9
fig, axe = plotter.boxplot(
		raceID = (season, race), 
		driverIDList = driverIDList, 
		startLap = 0, endLap = None, exclude=1.05)
plt.show()
```
![Example of a 'boxplot' for the 2024 Canadian Grand Prix](https://github.com/rebruno/F1Plotter/assets/101484447/a5e3add6-80de-483d-b3a6-2eb619e615fd)

## Testing
Tests are in the ```tests``` folder. Compatible with Python's unittest framework and pytest.
