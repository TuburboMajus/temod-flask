from flask import Response
from .exceptions import *

import json 

def rest_endpoint(class_):

	def __endpoint(*args,**kwargs):
		executioneer = class_(*args,**kwargs)
		encoder = getattr(class_,"ENCODER",lambda x:{"data":json.dumps(x)})
		error_encoder = getattr(class_,"ERROR_ENCODER",lambda x:{"error":json.dumps(x)})
		try:
			response = executioneer()
			if type(response) == tuple:
				return Response(status=response[0], response=encoder(response[1]))
			return Response(status=200, response=encoder(response))
		except RestException:
			return Response(status=exc.status, response=error_encoder(exc.response))
		except:
			raise

	__endpoint.__name__ = class_.__name__
	return __endpoint
