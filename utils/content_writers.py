def dictifier(data):

	if type(data) in (list, tuple, set):
		return [dictifier(subdata) for subdata in data]
	elif type(data) is dict:
		return {k:dictifier(v) for k,v in data.items()}
	else:
		if hasattr(data, "to_dict"):
			return data.to_dict()
		else:
			return data