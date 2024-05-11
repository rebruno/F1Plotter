# F1Plotter
Python module to call from Ergast API, with plotting capabilities.

##Installation: 
Run 
``` 
python -m build
pip install --find-links install dist\f1plotter-0.0.1-py3-none-any.whl
``` 
in the same directory as ```pyproject.toml```.
The library can then be used through ```import f1plotter```.


##Classes
### APIRequester
Currently supports getting race names, results, driver, qualifying and lap information.<br>
Any call must have the race specified. An example of using follows, where get_laps() can also be any other _get_ function.<br>
``` 
requester = APIRequester()
requester.race(_season_, _round_)
laps = request.get_laps()
```

### Plotter
Need to import dataformatter and pass it in.<br>
Currently, only head_to_head_laptime() is supported. 

``` 
from f1plotter.plotter import *
from f1plotter.dataformatter import *

plotter = Plotter(DataFormatter())
driverIDList = ["max_verstappen", "leclerc", "perez"]
season = 2023
race = 1
fig, axe = plotter.head_to_head_laptime(raceID = (season, race), 
					driverIDList = driverIDList, 
					startLap = 0, endLap = None)
plt.show()

```
