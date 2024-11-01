from temod.base import Entity, Join, Cluster 
from temod.storage import REGISTRED_STORAGES
from temod.base.attribute import UUID4Attribute

from datetime import datetime
from uuid import uuid4

from .exceptions import *



def TemodDefaultTokenGenerator():
	return {"token":UUID4Attribute.generate_random_value(), "expiration_date":None}
		

class TemodUserHandler(object):
	"""docstring for TemodUserHandler"""
	def __init__(self, user_class, database_type, identifier="id", logins=None, is_authenticated_attr="is_authenticated", is_active_attr= "is_active", 
		token_attr="token", token_expiration_attr="expiration_date", token_generator=TemodDefaultTokenGenerator, **db_credentials):
		super(TemodUserHandler, self).__init__()
		self.user_class = user_class
		self.is_authenticated_attr = is_authenticated_attr
		self.is_active_attr = is_active_attr
		self.token_attr = token_attr
		self.token_expiration_attr = token_expiration_attr
		self.token_generator = token_generator
		self.db_credentials = db_credentials
		self.identifier = identifier
		self.logins = [] if logins is None else logins
		try:
			if issubclass(user_class,Entity):
				self.database = REGISTRED_STORAGES[database_type][Entity]
			elif issubclass(user_class,Join):
				self.database = REGISTRED_STORAGES[database_type][Join]
			elif issubclass(user_class,Cluster):
				self.database = REGISTRED_STORAGES[database_type][Cluster]
			else:
				raise
		except:
			raise Exception(f"Cannot pick the right database for user class {user_class} and database {database}")

	def load_user(self,x):
		dct = {self.identifier:x}
		user = self.database(self.user_class,**self.db_credentials).get(**dct)
		if user is not None:
			return TemodUser(user,identifier=self.identifier)

	def load_user_by_token(self,token):
		dct = {self.token_attr:token}
		user = self.database(self.user_class,**self.db_credentials).get(**dct)
		if user is not None:
			if user[self.token_expiration_attr] is None or user[self.token_expiration_attr] > datetime.now():
				user[self.is_authenticated_attr] = True
				user[self.is_active_attr] = True
				return TemodUser(user,identifier=self.identifier)
			user.takeSnapshot()
			user[self.token_attr] = None
			user[self.token_expiration_attr] = None
			self.database(self.user_class,**self.db_credentials).updateOnSnapshot(user)
		return None

	def search_user(self,*logins):
		if len(logins) > len(self.logins):
			raise TemodLoginsException("There is more logins than expected")
		elif len(logins) < len(self.logins):
			raise TemodLoginsException("Some logins are missing")
		user = self.database(self.user_class,**self.db_credentials).get(
			**{self.logins[i]:logins[i] for i in range(len(logins))}
		)
		if user is not None:
			return TemodUser(user,identifier=self.identifier)

	def login_user(self,temod_user):
		temod_user.user.takeSnapshot()
		temod_user[self.is_authenticated_attr] = True
		temod_user[self.is_active_attr] = True
		return self.database(self.user_class,**self.db_credentials).updateOnSnapshot(temod_user.user)

	def logout_user(self,temod_user):
		temod_user.user.takeSnapshot()
		temod_user[self.is_authenticated_attr] = False
		temod_user[self.is_active_attr] = False
		return self.database(self.user_class,**self.db_credentials).updateOnSnapshot(temod_user.user)

	def generate_token(self,temod_user):
		temod_user.user.takeSnapshot()
		generated = self.token_generator()
		temod_user[self.token_attr] = generated[self.token_attr]
		temod_user[self.token_expiration_attr] = generated[self.token_expiration_attr]
		self.database(self.user_class,**self.db_credentials).updateOnSnapshot(temod_user.user)
		return generated



class TemodUser(object):
	"""docstring for TemodUser"""
	def __init__(self,user,identifier="id"):
		super(TemodUser, self).__init__()
		self.identifier = identifier
		self.user = user

	def __getattribute__(self,name):
		if name != "user":
			try:
				return self.user[name]
			except:
				pass
		try:
			return super(TemodUser,self).__getattribute__(name)
		except:
			return getattr(self.user,name)

	def get_id(self):
		return self.user[self.identifier]

	@property
	def is_anonymous(self):
		return self.user is None

	def __getitem__(self,name):
		return self.user[name]

	def __setitem__(self,name,value):
		self.user[name] = value