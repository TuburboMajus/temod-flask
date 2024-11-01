class RestException(Exception):
	def __init__(self, status, response):
		super(RestException, self).__init__()
		self.status = status
		self.response = response
		