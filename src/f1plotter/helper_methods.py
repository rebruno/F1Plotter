def get_sec(times):
	try:
		m,s = times.split(":")
	except ValueError:
		return 0
	return round(int(m)*60 + float(s), 4)


driverColors = {
    "max_verstappen":   "darkorange",
    "leclerc":          "red",
    "perez":            "blue",
    "sainz":            "gold",
    "hamilton":         "darkorchid",
    "russell":          "aqua",
    "ricciardo":        "hotpink",
    "norris":           "yellow",
    "michael_schumacher":"red",
    "alonso":           "deepskyblue"
}

def get_driver_color(driverID):
    """
    If the driver doesn't have a color assigned to them already, randomly generates one.
    """
    if driverID not in driverColors.keys(): 
        color = colors.hsv_to_rgb((np.random.randint(0, 256)/256, 1, 1))
    else:
        color = driverColors[driverID]
    return color