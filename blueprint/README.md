# Temod Configurable Blueprints Documentation

Temod's configurable blueprints are introduced to induce more flexibility to Flask's blueprint and allow them to be
easier to transport from one project to another just by tuning the blueprint's configuration without changing the code in 
itself

## Blueprint

The basic configurable blueprint inherits from Flask's Blueprint object.

### Constructor

*__init__(self, &ast;args, default_config=None, &ast;&ast;kwargs)* : &ast;args and &ast;&ast;kwargs will be passed to the parent class flask.Blueprint

### Attributes

- **default_configuration**: A dictionnary containing the default configuration for the blueprint. Can be defined using the default_config argument in the *Blueprint* constructor or using the method *default_config(self, configuration)*
- **configuration**: A dictionnary representing the actual configuration of the Blueprint

### Methods

- **default_config(self, configuration)**: Sets the attribute *default_configuration* to *configuration*
- **setup(self, configuration)**: updates the *default_configuration* dictionnary with the values in *configuration*
- **get_configuration(self, config, &ast;args, fetch_from_app=True)**: gets the value represented by *config* from the blueprints config. If it fails to do so and *fetch_from_app* is set to *True*, the method attempts to fetch the configuration from the object *current_app.config*. If both previous attempt fail and *args* is not empty, the first value of *args* will be returned, otherwise a *ConfigNotFound* Exception will be raised.



## MultiLanguageBlueprint

This blueprint is a subclass of Blueprint and allows the selection of the language and the correspondant dictionnary on user request and session. Languages can be either string values ("en", "fr", "ar", ... ) or Objects. The dictionnary is a mapping of strings with the following format:

```json
{
	"en": { dictionnary relative to the english language },
	"fr": { dictionnary relative to french },
	...
}
```
This dictionnary must be included in either the app's configuration (app.config) or in the blueprint's configuration.
If you're using Objects as representatives for languages, you'll need to store them as well in either the app's configuration or the blueprint's configurations. Example:

```python
class Language:
	def __init__(self, code, name):
		self.code = code
		self.name = name

# Storing languages in the app config
app.config['LANGUAGES'] = {
	"en": Language("en","English"),
	"fr": Language("fr","Français"),
	...
}
```

*__init__(self, &ast;args, language_param='lg', default_language=None, default_language_picker=None, on_language_change=None, dictionnary_selector=None, &ast;&ast;kwargs)* : &ast;args and &ast;&ast;kwargs will be passed to the parent class Blueprint

### Attributes
- **language_param**: the language query parameter name ( default: 'lg'). Can be set in the constructor. Example: if the request recieved is "http://127.0.0.1:8080?lg=en", the blueprint will get the language associated with the str *en*
- **default_language**: a string representing the default language (default: None)
- **default_language_picker**: a callable object that takes no argument and returns the string representative of a language (en, fr, ...). It gets called if there is no language specified in the request query or in the current session. (default: returns the *default_language* attribute). Per example: If no language is specified in the request or the session, this function can be useful to pick the language from the current_user object.
- **on_language_change**: A callable object that gets called when the language changes and takes a single parameter. A language change occurs when it is picked from the request query 
- **dictionnary_selector**: A callable object that gets called when selecting a dictionnary. This is useful when using Objects as representatives for languages. Per example, using the class *Language* defined above, the proper *dictionnary_selector* would be *lambda x:x.code* 

### Constants

- **LANGUAGES_KEY**: the configuration name to use to get the languages dict from the app's or the blueprint's configuration (default: 'LANGUAGES')
- **DICTIONNARY_KEY**: the configuration name to use to get the dictionnary from the app's or the blueprint's configuration (default: 'DICTIONNARY') 

### Methods

- **_get_str_language(self, return_language_only=True)**: Returns the string representing the language trying to pick from to the current request, then the session if it fails, if it fails again, it calls *default_language_picker()*. if *default_language_picker()* returns None, this methods tries last to pick the configuration "default_language" from either thje blueprint's or the app's config. if *return_language_only* is set to False, this method returns 3 values: the language, is_default (True if not found in request or session) and has_changed (if the language is picked from the request) otherwise, thos method just returns the language. This method doesn't fire the *on_language_change* callback.
- **get_language(self)**: Returns the representative of the language with the same order of selection as the previous method. If the app's or the blueprint's configurations have no config name *'LANGUAGES'* (or whatever you set the constant *LANGUAGES_KEY* to) this function will return the string representative of the language. This method does fire the *on_language_change*
- **get_dictionnary(self)**: Returns the dictionnary correspondant to the language returned by the method *get_language*

### Decorators

- **with_language** : Can be used to decorate a flask endpoint an loads automatically the language of the current caller using *get_language*. 
- **with_dictionnary** : Can be used to decorate a flask endpoint an loads automatically the language and the correspondant dictionnary of the current caller using *get_dictionnary*. 

### Example Of Usage:

index.html
```html
<html>
	<body>
		{{dictionnary['string_1'].title()}}, {{dictionnary['string_2']}}: "{{language.name}}"
	</body>
</html>
```

The blueprint 

```python
class Language:
	def __init__(self, code, name):
		self.code = code
		self.name = name

blueprint = MultiLanguageBlueprint('test', __name__, dictionnary_selector=lambda lg:lg.code,default_config={
	"LANGUAGES": [Language("en","English"),Language("fr","Français")],
	"DICTIONNARY": {
		"en": {"string_1":"hello", "string_2": "you've chosen"},
		"fr": {"string_1":"salut", "string_2": "vous avez choisi"},
	}
	"default_language": "en", 
})

@blueprint.route('/home')
def home():
	# Get the language of the page
	language = blueprint.get_language()
	# Get the dictionnary
	dictionnary = blueprint.get_dictionnary()

	return render_tempalte("index.html",dictionnary=dictionnary, language=language)
```

After registering this blueprint to your app and running it (let say on http://127.0.0.1:5000) you'll have the following responses:

- GET 127.0.0.1:5000 returns 
```
<html>
	<body>
		Hello, you've chosen: "English"
	</body>
</html>
```

- GET 127.0.0.1:5000?lg=fr returns 
```
<html>
	<body>
		Bonjour, vous avez choisi: "Français"
	</body>
</html>
```

- Another GET call to 127.0.0.1:5000 (without the lg query parameter) returns 
```
<html>
	<body>
		Bonjour, vous avez choisi: "Français"
	</body>
</html>
```
This last call will not change back to english since the chosen language for your session has been set to "fr" on the previous one 


Using decorators: The same result can be achieved if the *home* route was defined as follows:
```python
@blueprint.route('/home')
@with_dictionnary
def home(language, dictionnary):
	return render_tempalte("index.html",dictionnary=dictionnary, language=language)
```

