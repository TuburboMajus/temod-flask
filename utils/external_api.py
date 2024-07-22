from flask_login import current_user

from temod_open_api.endpoint import METHODS
from temod_open_api import Api

from datetime import datetime
from enum import Enum



def register_api(name, api):
	return APIS_REGISTER.register(name, api)


class ApisRegister(object):
	"""docstring for ApisRegister"""
	def __init__(self):
		super(ApisRegister, self).__init__()
		self.apis = {}

	def register(self, name, api):
		if name in self.apis:
			raise Exception(f"Another api is already registred with name {name}")
		self.apis[name] = api

	def __contains__(self, name):
		return name in self.apis
		

class ApiCaller(object):
	"""docstring for ApiCaller"""
	def __init__(self, name, rate_limiter=None):
		super(ApiCaller, self).__init__()
		if name not in APIS_REGISTER:
			raise Exception(f"No api have been registered with name {name}")
		self.api = APIS_REGISTER.apis[name]
		self.endpoint = None
		self.rate_limiter = rate_limiter

	def __getitem__(self, endpoint, *args, **kwargs):
		return EndpointCaller(self.api[endpoint], self.rate_limiter,*args, **kwargs)


class EndpointCaller(object):
	"""docstring for EndpointCaller"""
	def __init__(self, endpoint, rate_limiter, *args, **kwargs):
		super(EndpointCaller, self).__init__()
		self.rate_limiter = rate_limiter
		self.endpoint = endpoint
		self.args = args
		self.kwargs = kwargs
		self.method = None

	def wrapper(self, params=None):

		if params is None:
			params = {}
		
		callable_params = False
		if hasattr(params,"__call__"):
			callable_params = True

		def __callback(wrapped):
			def __doCall(*args, **kwargs):
				extra = []
				if self.rate_limiter is not None:
					rate_limit = self.rate_limiter()
					if rate_limit is not None and rate_limit.limited:
						return wrapped(None,rate_limit,*args, **kwargs)
					extra.append(rate_limit)
				endpoint = self.endpoint(
					*[(arg(*args, **kwargs) if hasattr(arg,"__call__") else arg) for arg in self.args],
					**{k:(v(*args, **kwargs) if hasattr(v,"__call__") else v) for k,v in self.kwargs.items()} 
				)
				if callable_params:
					return wrapped(getattr(endpoint, self.method)(**params(*args, **kwargs)),*extra,*args, **kwargs)		
				return wrapped(getattr(endpoint, self.method)(
					**{k:(v(*args, **kwargs) if hasattr(v,"__call__") else v) for k,v in params.items()}
				),*extra,*args, **kwargs)

			__doCall.__name__ = wrapped.__name__
			return __doCall

		return __callback

	def __getattribute__(self, name):
		if name in METHODS.__members__:
			self.method = name
			print(self.wrapper)
			return self.wrapper
		return super(EndpointCaller, self).__getattribute__(name)


RATE_LIMIT_UNITS = Enum('RATE_LIMIT_UNITS',["second","minute","hour","day","month"])
RATE_LIMIT_VALUES = {
	RATE_LIMIT_UNITS.second:1,
	RATE_LIMIT_UNITS.minute:60,
	RATE_LIMIT_UNITS.hour:3600,
	RATE_LIMIT_UNITS.day:86400
}


class RateLimit(object):
	"""docstring for RateLimit"""
	def __init__(self, counter, count, left, limited):
		super(RateLimit, self).__init__()
		self.counter = counter
		self.count = count
		self.left = left
		self.limited = limited


class RateLimiter(object):
	"""docstring for RateLimiter"""
	def __init__(self, counter, limit=5, unit="minute"):
		super(RateLimiter, self).__init__()
		self.counter = counter
		self.limit = max(1,int(limit))
		if issubclass(type(unit),RATE_LIMIT_UNITS):
			self.unit = unit
		else:
			try:
				self.unit=RATE_LIMIT_UNITS(unit)
			except:
				self.unit=RATE_LIMIT_UNITS[unit]

	def __call__(self):
		since, count = self.counter.increment() 
		now = datetime.now()
		delta = (now-since).total_seconds()
		if self.unit != RATE_LIMIT_UNITS.month:
			if delta <= RATE_LIMIT_VALUES[self.unit]:
				return RateLimit(self.counter,count,max(0,self.limit-count),count > self.limit)
		else:
			if since.month == now.month and since.year == now.year:
				return RateLimit(self.counter,count,max(0,self.limit-count),count > self.limit)

		self.counter.reset()
		return RateLimit(self.counter,1,max(0,self.limit-1),False)

class CurrentUserLimiter(RateLimiter):
	"""docstring for CurrentUserLimiter"""
	def __init__(self, counter_loader, limit=5, unit="minute"):
		super(CurrentUserLimiter, self).__init__(counter_loader, limit=limit, unit=unit)

	def __call__(self):
		counter = self.counter(current_user)
		if counter is None:
			return None
		since, count = counter.increment() 
		now = datetime.now()
		delta = (now-since).total_seconds()
		if self.unit != RATE_LIMIT_UNITS.month:
			if delta <= RATE_LIMIT_VALUES[self.unit]:
				return RateLimit(counter,count,max(0,self.limit-count),count > self.limit)
		else:
			if since.month == now.month and since.year == now.year:
				return RateLimit(counter,count,max(0,self.limit-count),count > self.limit)

		counter.reset()
		return RateLimit(counter,1,max(0,self.limit-1),False)


		

__builtins__['APIS_REGISTER'] = ApisRegister()
		
