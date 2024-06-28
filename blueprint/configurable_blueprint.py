from flask import Blueprint as flaskBlueprint, current_app, request, session
from .exceptions import *


class Blueprint(flaskBlueprint):
	"""docstring for Blueprint"""
	def __init__(self, *args, default_config=None, **kwargs):
		super(Blueprint, self).__init__(*args, **kwargs)
		self.default_configuration = {} if default_config is None else default_config
		self.default_config(self.default_configuration)

	def default_config(self, configuration):
		try:
			self.default_configuration = dict(configuration)
		except:
			raise WrongConfigurationFormat("Blueprint configuration must be a dictionnary or an object transformable into a dictionnary using dict()")
		return self

	def setup(self, configuration):
		default = dict(self.default_configuration)
		self.configuration = {
			key: configuration.get(key, value) for key,value in default.items()
		}
		self.configuration.update(configuration)
		return self

	def get_configuration(self, config, *args, fetch_from_app=True):
		has_default = False
		if( len(args) > 0 ):
			has_default = True
			default = args[0]

		try:
			return self.configuration[config]
		except:
			if not hasattr(self,"configuration"):
				self.setup({})
				return self.get_configuration(config)
			try:
				if fetch_from_app:
					return getattr(current_app, 'config', {})[config]
			except:
				if has_default:
					return default
			raise ConfigNotFound(f"Nor the blueprint nor the app have the config: {config}")


class MultiLanguageBlueprint(Blueprint):
	"""docstring for MultiLanguageBlueprint"""

	LANGUAGES_KEY = "LANGUAGES"
	DICTIONNARY_KEY = "DICTIONNARY"

	def __init__(self, *args, language_param='lg', default_language=None, default_language_picker=None, on_language_change=None, dictionnary_selector=None,
		**kwargs):
		super(MultiLanguageBlueprint, self).__init__(*args, **kwargs)
		self.language_param = language_param
		self.default_language = default_language
		self.on_language_change = lambda x:x if on_language_change is None else on_language_change
		if not hasattr(self.on_language_change,'__call__'):
			raise CallbackException("on_language_change needs to be a callable object that takes one str argument")
		self.default_language_picker = lambda :self.default_language if default_language_picker is None else default_language_picker
		if not hasattr(self.default_language_picker,'__call__'):
			raise CallbackException("default_language_picker needs to be a callable object that takes no argument")
		self.dictionnary_selector = (lambda x:x) if dictionnary_selector is None else dictionnary_selector
		if not hasattr(self.dictionnary_selector,'__call__'):
			raise CallbackException("dictionnary_selector needs to be a callable object that takes one argument")

	def setup(self, configuration):
		if "language_param" in configuration:
			self.language_param = configuration["language_param"]
		if "default_language" in configuration:
			self.default_language = configuration["default_language"]
		return super(MultiLanguageBlueprint, self).setup(configuration)

	def _get_str_language(self, return_language_only=True):
		lg = request.args.get(self.language_param)
		is_default = False
		has_changed = False

		if lg is None:
			lg = session.get(self.language_param)
			if lg is None:
				lg = self.default_language_picker()
				if lg is None:
					try:
						lg = self.get_configuration("default_language",None)
					except:
						pass
				is_default = True
		else:
			session[self.language_param] = lg
			has_changed = True

		if not return_language_only:
			return lg, is_default, has_changed
		return lg

	def get_language(self):
		lg, is_default, has_changed = self._get_str_language(return_language_only=False)

		languages = self.get_configuration(MultiLanguageBlueprint.LANGUAGES_KEY,None)
		if languages is None:
			if has_changed:
				self.on_language_change(lg)
			return lg

		try:
			language = languages[lg]
			if has_changed:
				self.on_language_change(language)
			return language
		except:
			if not is_default:
				lg = self.default_language_picker()
				return languages[lg]
			raise LanguageNotFound("The default language was not properly set")


	def get_dictionnary(self):
		language = self.get_language()
		return self.get_configuration(MultiLanguageBlueprint.DICTIONNARY_KEY).get(
			self.dictionnary_selector(language)
		)