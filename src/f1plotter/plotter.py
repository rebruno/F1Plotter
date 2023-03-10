from matplotlib import pyplot as plt
import numpy as np
import warnings

import base64
from io import BytesIO


class Plotter():
	def __init__(self, dataformatter):
		"""
		dataformatter is a DataFormatter class, as specified in dataformatter.py. Must be initialized when passed
			
		"""

		self.dataformatter = dataformatter

	def get_plot(self):
		fig = plt.figure()
		axe = plt.axes()

		axe.grid(linestyle="--", linewidth=0.5)

		return fig, axe

	def head_to_head_laptime(self, raceID, driverIDList, startLap = 0, endLap = None):
		"""
		raceID is a way to identify the race. This depends on how DataFormatter is implemented.
		For this, raceID = (season, round_number)

		driverIDList is a list of driver IDs used in the API, season is a year, round_number is the race number
		
		startLap and endLap can be used to specify a lap window(ex: from lap 15 to 24)

		To be implemented: laps, cutoff, delta_plot
		"""

		fig, laptimesAxe = self.get_plot()
		data = self.dataformatter 
		lapTimeData = data.get_laps(raceID, driverIDList, startLap = startLap, endLap = endLap)


		for driver in driverIDList:
			laptimesAxe.scatter(lapTimeData[driver]["lap"], lapTimeData[driver]["laptime"], label=driver)

		laptimesAxe.set_xlabel("Lap number")
		laptimesAxe.set_ylabel("Lap times [s]")
		
	
		laptimesAxe.set_title("{}".format(data.get_racename(raceID)))

		x_min, x_max = laptimesAxe.get_xlim()
		laptimesAxe.set_xticks([i for i in range(round(x_min), round(x_max), 5)])
		
		#median_time = np.median([np.median(laptime["laptime"]) for laptime in lapTimeData.values()])
		

		laptimesAxe.legend()
		return fig, laptimesAxe

	
	def boxplot(raceID, driverIDList, startLap = 0, endLap = None, exclude = -1, scatter = True):
		pass


	def show(self):
		plt.show()

	@classmethod
	def get_html_embed(cls, fig):
		"""
		https://stackoverflow.com/questions/48717794/matplotlib-embed-figures-in-auto-generated-html
		Generates temporary file to then embed it as html.
		Will be used for embedding the plot generated by matplotlib in another project
		"""
		tmpfile = BytesIO()
		
		fig.savefig(tmpfile, format='png')
		encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

		html = "<img src = \'data:image/png;base64,{}\'>".format(encoded)

		return html

