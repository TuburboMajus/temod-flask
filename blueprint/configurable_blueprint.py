from flask import Blueprint as flaskBlueprint, Response, current_app, request, session, g
from .exceptions import *

import random, string


class Blueprint(flaskBlueprint):
    """
    A blueprint class extending Flask's Blueprint to include default configuration handling.
    """

    def __init__(self, *args, default_config=None, **kwargs):
        """
        Initialize the Blueprint with default configuration.

        :param default_config: Default configuration dictionary.
        """
        super(Blueprint, self).__init__(*args, **kwargs)
        self.default_configuration = {} if default_config is None else default_config
        self.default_config(self.default_configuration)

    def default_config(self, configuration):
        """
        Set the default configuration for the blueprint.

        :param configuration: Configuration dictionary.
        :return: Self for method chaining.
        """
        try:
            self.default_configuration = dict(configuration)
        except:
            raise WrongConfigurationFormat("Blueprint configuration must be a dictionary or an object transformable into a dictionary using dict()")
        return self

    def setup(self, configuration):
        """
        Setup the blueprint with the provided configuration, merging it with the default configuration.

        :param configuration: Configuration dictionary.
        :return: Self for method chaining.
        """
        default = dict(self.default_configuration)
        self.configuration = {
            key: configuration.get(key, value) for key, value in default.items()
        }
        self.configuration.update(configuration)
        return self

    def get_configuration(self, config, *args, fetch_from_app=True):
        """
        Get the configuration value for the specified key.

        :param config: Configuration key.
        :param args: Optional default value if the configuration key is not found.
        :param fetch_from_app: Flag to fetch configuration from the Flask app if not found in the blueprint.
        :return: Configuration value.
        :raises: ConfigNotFound if the configuration key is not found and no default is provided.
        """
        has_default = False
        if len(args) > 0:
            has_default = True
            default = args[0]

        try:
            return self.configuration[config]
        except:
            if not hasattr(self, "configuration"):
                self.setup({})
                return self.get_configuration(config)
            try:
                if fetch_from_app:
                    return getattr(current_app, 'config', {})[config]
            except:
                if has_default:
                    return default
            raise ConfigNotFound(f"Neither the blueprint nor the app have the config: {config}")

    def split_route(self,routes, *rargs, **rkwargs):

        def __formatter(func):
            def __fwrapper(route):
                def route_function(*args,**kwargs):
                    results = route(*args, **kwargs)
                    if type(results) is Response:
                        return results
                    return func(*results)

                route_function.__name__ = route.__name__+''.join(random.choices(string.ascii_letters + string.digits, k=10))
                return route_function
            return __fwrapper

        def __wrapper(f):
            for route, formatter in routes.items():
                self.route(route,*rargs, **rkwargs)(__formatter(formatter)(f))
                print(f"Route {route} has been registered")

        return __wrapper





class MultiLanguageBlueprint(Blueprint):
    """
    A blueprint class to manage multi-language support in a Flask application.
    """

    LANGUAGES_KEY = "LANGUAGES"
    DICTIONNARY_KEY = "DICTIONNARY"

    def __init__(self, *args, language_param='lg', default_language=None, default_language_picker=None, on_language_change=None, 
                 dictionnary_selector=None, load_in_g=None, **kwargs):
        """
        Initialize the MultiLanguageBlueprint with parameters for language management.

        :param language_param: Parameter name to use for language in requests.
        :param default_language: Default language if none is provided.
        :param default_language_picker: Callable to determine default language.
        :param on_language_change: Callable to handle language change events.
        :param dictionnary_selector: Callable to select dictionary based on language.
        :param load_in_g: Flag to load language and dictionary in Flask global `g`.
        """
        super(MultiLanguageBlueprint, self).__init__(*args, **kwargs)
        self.language_param = language_param
        self.default_language = default_language
        self.on_language_change = (lambda x: x) if on_language_change is None else on_language_change

        # Ensure on_language_change is callable
        if not hasattr(self.on_language_change, '__call__'):
            raise CallbackException("on_language_change needs to be a callable object that takes one str argument")
        
        self.default_language_picker = lambda: self.default_language if default_language_picker is None else default_language_picker
        
        # Ensure default_language_picker is callable
        if not hasattr(self.default_language_picker, '__call__'):
            raise CallbackException("default_language_picker needs to be a callable object that takes no argument")
        
        self.dictionnary_selector = (lambda x: x) if dictionnary_selector is None else dictionnary_selector
        
        # Ensure dictionnary_selector is callable
        if not hasattr(self.dictionnary_selector, '__call__'):
            raise CallbackException("dictionnary_selector needs to be a callable object that takes one argument")

        self.load_in_g = load_in_g

    def setup(self, configuration):
        """
        Setup the blueprint with configuration settings.

        :param configuration: Configuration dictionary.
        """
        if "language_param" in configuration:
            self.language_param = configuration["language_param"]
        if "default_language" in configuration:
            self.default_language = configuration["default_language"]
        return super(MultiLanguageBlueprint, self).setup(configuration)

    def _get_str_language(self, return_language_only=True):
        """
        Retrieve the current language setting.

        :param return_language_only: Flag to return only the language.
        :return: Language code (and additional flags if return_language_only is False).
        """
        lg = request.args.get(self.language_param)
        is_default = False
        has_changed = False

        if lg is None:
            lg = session.get(self.language_param)
            if lg is None:
                lg = self.default_language_picker()
                if lg is None:
                    try:
                        lg = self.get_configuration("default_language", None)
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
        """
        Get the current language, triggering change event if necessary.

        :return: Current language.
        """
        lg, is_default, has_changed = self._get_str_language(return_language_only=False)
        languages = self.get_configuration(MultiLanguageBlueprint.LANGUAGES_KEY, None)
        
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

    def get_dictionnary(self, return_dictionnary_only=True):
        """
        Get the dictionary for the current language.

        :param return_dictionnary_only: Flag to return only the dictionary.
        :return: Dictionary (and language if return_dictionnary_only is False).
        """
        language = self.get_language()
        dictionnary = self.get_configuration(MultiLanguageBlueprint.DICTIONNARY_KEY).get(
            self.dictionnary_selector(language)
        )
        if return_dictionnary_only:
            return dictionnary
        return language, dictionnary

    def with_language(self, f):
        """
        Decorator to inject the current language into the function.

        :param f: Function to decorate.
        :return: Decorated function.
        """
        def __load_language(*args, **kwargs):
            language = self.get_language()
            if self.load_in_g in [None, True]:
                g.language = language
            if self.load_in_g in [None, False]:
                return f(language, *args, **kwargs)
            return f(*args, **kwargs)

        __load_language.__name__ = f.__name__
        return __load_language

    def with_dictionnary(self, f):
        """
        Decorator to inject the current language and dictionary into the function.

        :param f: Function to decorate.
        :return: Decorated function.
        """
        def __load_dictionnary(*args, **kwargs):
            language, dictionnary = self.get_dictionnary(return_dictionnary_only=False)
            if self.load_in_g in [None, True]:
                g.language = language
                g.dictionnary = dictionnary
            if self.load_in_g in [None, False]:
                return f(language, dictionnary, *args, **kwargs)
            return f(*args, **kwargs)

        __load_dictionnary.__name__ = f.__name__
        return __load_dictionnary
