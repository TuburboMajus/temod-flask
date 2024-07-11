# Temod's Blueprints

The `MultiLanguageBlueprint` class extends Flask's `Blueprint` to add multi-language support for your application. This class, along with the `Blueprint` class it extends, allows you to manage configurations and handle multiple languages seamlessly.

## Usage

### Blueprint Class

The `Blueprint` class provides a base for handling configurations in your Flask blueprints.

#### Example

```python
from temod_flask import Blueprint

app = Flask(__name__)

# Initialize the Blueprint with a default configuration
default_config = {
    'example_key': 'example_value'
}
blueprint = Blueprint('example_blueprint', __name__, default_config=default_config)

# Setup additional configurations
blueprint.setup({
    'another_key': 'another_value'
})

@app.route('/')
def index():
    # Access configuration
    example_value = blueprint.get_configuration('example_key')
    return f'Example Value: {example_value}'

app.register_blueprint(blueprint)
```

### MultiLanguageBlueprint Class

The `MultiLanguageBlueprint` class extends the `Blueprint` class to handle multi-language support.

#### Parameters

- `language_param`: The parameter name to use for language in requests.
- `default_language`: The default language if none is provided.
- `default_language_picker`: A callable to determine the default language.
- `on_language_change`: A callable to handle language change events.
- `dictionnary_selector`: A callable to select the dictionary based on the language.
- `load_in_g`: A flag to load the language and dictionary in Flask's global `g`.

#### Example

```python
from your_module import MultiLanguageBlueprint

app = Flask(__name__)

# Initialize the MultiLanguageBlueprint with configurations
multi_lang_blueprint = MultiLanguageBlueprint('multi_lang_blueprint', __name__,
                                              language_param='lang',
                                              default_language='en',
                                              on_language_change=lambda lang: print(f'Language changed to {lang}'),
                                              dictionnary_selector=lambda lang: f'dict_{lang}')

# Setup additional configurations
multi_lang_blueprint.setup({
    'LANGUAGES': {
        'en': 'English',
        'fr': 'French'
    },
    'DICTIONNARY': {
        'dict_en': {'hello': 'Hello'},
        'dict_fr': {'hello': 'Bonjour'}
    }
})

@app.route('/')
@multi_lang_blueprint.with_language
def index(language):
    return f'Current Language: {language}'

@app.route('/greet')
@multi_lang_blueprint.with_dictionnary
def greet(language, dictionnary):
    greeting = dictionnary.get('hello', 'Hi')
    return f'Greeting: {greeting}'

app.register_blueprint(multi_lang_blueprint)
```

### Methods

#### Blueprint

- `default_config(configuration)`: Set the default configuration for the blueprint.
- `setup(configuration)`: Setup the blueprint with the provided configuration, merging it with the default configuration.
- `get_configuration(config, *args, fetch_from_app=True)`: Get the configuration value for the specified key.

#### MultiLanguageBlueprint

- `setup(configuration)`: Setup the blueprint with configuration settings.
- `_get_str_language(return_language_only=True)`: Retrieve the current language setting.
- `get_language()`: Get the current language, triggering change event if necessary.
- `get_dictionnary(return_dictionnary_only=True)`: Get the dictionary for the current language.
- `with_language(f)`: Decorator to inject the current language into the function.
- `with_dictionnary(f)`: Decorator to inject the current language and dictionary into the function.

## Error Handling

The classes raise specific exceptions for configuration errors:

- `CallbackException`: Raised when a required callback is not callable.
- `WrongConfigurationFormat`: Raised when the configuration format is incorrect.
- `ConfigNotFound`: Raised when a requested configuration key is not found.
- `LanguageNotFound`: Raised when the default language is not properly set.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -am 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a new Pull Request.

## Acknowledgments

- PyAxolotl: abdellatifzied.saada@gmail.com (Author)
- Inspiration and ideas from the Flask community.