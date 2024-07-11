
# Paginator

The `Paginator` class handles pagination of entities retrieved from storage. This class works with the `Blueprint` class to manage configurations and perform pagination in your application.

## Usage

### Pagination Class

The `Pagination` class handles the pagination logic.

#### Example

```python
from temod_flask import Pagination

# Initialize the Pagination object
pagination = Pagination(current_item, current_page_number, total_number_of_pages)

print(pagination.current)  # Access the current item
print(pagination.current_page)  # Access the current page number
print(pagination.total_pages)  # Access the total number of pages
```

### Paginator Class

The `Paginator` class works with the `Blueprint` class to handle pagination of entities.

#### Parameters

- `blueprint`: The blueprint instance for configuration.
- `page_arg_name`: The name of the query parameter for the current page.
- `page_size_arg_name`: The name of the query parameter for the page size.
- `page_size_config`: The configuration key for the page size.
- `listify`: Flag to convert elements to a list.
- `count_total`: Flag to count the total number of entities.

#### Example

```python
from your_module import Paginator, Blueprint

app = Flask(__name__)

# Initialize the Blueprint with a default configuration
default_config = {
    'page_size': 10
}
blueprint = Blueprint('example_blueprint', __name__, default_config=default_config)

# Initialize the Paginator with the blueprint
paginator = Paginator(blueprint)

# Setup the entity type and storage
class MyEntity:
    storage = MyStorageClass()  # Replace with your storage class

paginator.for_entity(MyEntity)

@app.route('/items')
@paginator.paginate
def get_items(pagination):
    items = pagination.current  # Get the current page of items
    return jsonify(items)

app.register_blueprint(blueprint)
```

### Methods

#### Pagination

- `__init__(current, current_page, total_pages=None)`: Initialize the Pagination object.

#### Paginator

- `__init__(blueprint, page_arg_name='page', page_size_arg_name=None, page_size_config="page_size", listify=True, count_total=True)`: Initialize the Paginator object.
- `for_entity(entity_type: Entity)`: Set the storage for the paginator based on the entity type.
- `from_storage(storage)`: Set the storage for the paginator.
- `with_filter(function)`: Set the filter function for the paginator.
- `paginate(f)`: Decorator to paginate the results of a function.

## Error Handling

The classes raise specific exceptions for configuration errors:

- `NoStorageConfigurated`: Raised when no storage is configured for the paginator.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -am 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a new Pull Request.

## Acknowledgments

- PyAxolotl: abdellatifzied.saada@gmail.com (Author)
- Inspiration and ideas from the Flask community.