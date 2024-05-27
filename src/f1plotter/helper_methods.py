def get_sec(times):
	try:
		m,s = times.split(":")
	except ValueError:
		return 0
	return round(int(m)*60 + float(s), 4)