# Change Log

## Version 2.2.3

### Authors

- PyAxolotl

### Additions

- Paginator: Include support for default fitlers for paginators (filter based on the paginated entity's attributes)
- Pagination: to_dict method

## Version 2.2.1

### Authors

- PyAxolotl

### Additions

- Added MultiAuthenticator: Authenticator allowing both session and token authentication 
- Added Rest Endpoints: Abstract definition of rest endpoints

### FIXES

- Fixed a bug where MultiLanguageBlueprint failed to update language on change

### Authors

- PyAxolotl

## Version 2.2.0

### Additions

- Added ApiRegister and ApiCaller object to add support for temod-open-api 

### Authors

- PyAxolotl

## Version 2.1.2

### Additions

- Added method orderby to Paginator to set the order paginated elements should be gathered in

### Authors

- PyAxolotl

## Version 2.1.1

### Additions

- MultiLanguageBlueprint now accepts load_in_g param
- Added class Paginator that allows to decorate flask enpoints for an easy pagination of entities stored in db

### Authors

- PyAxolotl

## Version 2.1.0

### Additions

- Adding with_dictionnary and with_language decorators to MultiLanguageBlueprint
- Authenticator allows now the 'remember' kwarg for the remember me functionnality

### FIXES

- Fixing a bug with content_readers.body_content function 

### Authors

- PyAxolotl

## Version 2.0.8

### Additions

- Introducing temod's configurable blueprints: Blueprint and MultiLanguageBlueprint
- Starting this changelog

### Authors

- PyAxolotl