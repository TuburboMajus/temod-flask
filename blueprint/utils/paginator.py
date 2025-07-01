from temod_flask.blueprint.utils.exceptions import *
from temod_flask.blueprint import Blueprint
from temod.base.condition import Equals
from temod.base import Entity, Join

from flask import request

import math


class Pagination(object):
    """
    A class to handle pagination logic.
    """

    def __init__(self, current, current_page, total_pages=None):
        """
        Initialize the Pagination object.

        :param current: The current item.
        :param current_page: The current page number.
        :param total_pages: The total number of pages, if known.
        """
        super(Pagination, self).__init__()
        self.total_pages = total_pages
        self.current_page = current_page
        self.current = current

    def to_dict(self, translator=None):
        dct = {
            "total_pages": self.total_pages,
            "current_page": self.current_page,
            "current": [element.to_dict() for element in self.current]
        }
        if translator is not None:
            return {translator.get(k,k):v for k,v in dct.items()}
        return dct



class Paginator(object):
    """
    A class to handle pagination of entities retrieved from storage.
    """

    def __init__(self, blueprint: Blueprint, page_arg_name='page', page_size_arg_name=None, page_size_config="page_size", 
                 listify=True, count_total=True):
        """
        Initialize the Paginator object.

        :param blueprint: The blueprint instance for configuration.
        :param page_arg_name: The name of the query parameter for the current page.
        :param page_size_arg_name: The name of the query parameter for the page size.
        :param page_size_config: The configuration key for the page size.
        :param listify: Flag to convert elements to a list.
        :param count_total: Flag to count the total number of entities.
        """
        super(Paginator, self).__init__()
        self.blueprint = blueprint
        self.page_arg_name = page_arg_name
        self.page_size_arg_name = page_size_arg_name
        self.page_size = blueprint.get_configuration(page_size_config)
        self.storage = None
        self.filter = None
        self.path_filter = None
        self.listify = listify
        self.default_filter = True
        self.count_total = count_total

    def for_entity(self, entity_type: Entity):
        """
        Set the storage for the paginator based on the entity type.

        :param entity_type: The entity type.
        :return: Self for method chaining.
        """
        if hasattr(entity_type, "storage"):
            self.entity_type = entity_type
            self.storage = entity_type.storage
        else:
            raise NoStorageConfigurated(f"No default storage has been set for entities of type {entity_type}. Use method 'from_storage'")
        return self

    def from_storage(self, storage):
        """
        Set the storage for the paginator.

        :param storage: The storage instance.
        :return: Self for method chaining.
        """
        self.storage = storage
        return self

    def with_default_filter(self,activate: bool):
        """
        Set the filter function for the paginator.

        :param function: The filter function.
        :return: Self for method chaining.
        """
        self.default_filter = activate
        return self

    def with_filter(self, function):
        """
        Set the filter function for the paginator.

        :param function: The filter function.
        :return: Self for method chaining.
        """
        self.filter = function
        return self

    def with_path_filter(self, function):
        """
        Set the filter function for the paginator.

        :param function: The filter function.
        :return: Self for method chaining.
        """
        self.path_filter = function
        return self

    def orderby(self, order):
        """
        Set the order of the paginated elements.

        :param function: The order string.
        :return: Self for method chaining.
        """
        self.order = order
        return self

    def __build_basic_conditions(self, args: dict):
        conditions = []
        if issubclass(self.entity_type, Entity):
            for arg, value in args.items():
                try:
                    attribute = [attr for attr in self.entity_type.ATTRIBUTES if attr['name'] == arg][0]
                    conditions.append(Equals(attribute['type'](arg,value=value)))
                except:
                    pass
        elif issubclass(self.entity_type, Join):
            try:
                entities = [self.entity_type.DEFAULT_ENTRY]
                for constraint in self.entity_type.STRUCTURE:
                    for entity in constraint.entities():
                        if not(entity.ENTITY_NAME in [e.ENTITY_NAME for e in entities]):
                            entities.append(entity)
            except:
                return []
            for arg, value in args.items():
                try:
                    for entity in entities:
                        try:
                            attribute = [attr for attr in entity.ATTRIBUTES if attr['name'] == arg][0]
                        except:
                            continue
                        conditions.append(Equals(attribute['type'](arg,value=value,owner_name=entity.ENTITY_NAME)))
                except:
                    pass
        return conditions


    def paginate(self, f):
        """
        Decorator to paginate the results of a function.

        :param f: The function to be paginated.
        :return: The decorated function.
        """

        if self.storage is None:
            raise NoStorageConfigurated("No storage for Paginator to retrieve entities from")

        def __gather_entities(*args, **kwargs):
            """
            Gather and paginate entities.

            :param args: Positional arguments for the function.
            :param kwargs: Keyword arguments for the function.
            :return: The function result with paginated entities.
            """
            try:
                current_page = int(request.args.get(self.page_arg_name, 1))
            except:
                current_page = 1

            if self.page_size_arg_name is not None:
                # TODO: Handle configurable page size
                pass

            total_pages = None
            filters = []; 
            if self.filter is not None:
                filters.append(self.filter(dict(request.args))); 
            if self.path_filter is not None:
                filters.append(self.path_filter(kwargs));
            filters = [result for result in filters if result is not None] 
            if self.default_filter:
                default_filters_ = self.__build_basic_conditions(dict(request.args))
            order = None
            if hasattr(self, "order"):
                order = self.order
                if self.order is not None and hasattr(self.order,"__call__"):
                    order = self.order(dict(request.args))
            elements = self.storage.list(*default_filters_,*filters,skip=(current_page-1)*self.page_size,limit=self.page_size,orderby=order)
            if self.count_total:
                total_count = self.storage.count(*default_filters_,*filters)
                total_pages = math.ceil(total_count/self.page_size)


            if self.listify:
                elements = list(elements)
                
            return f(Pagination(elements, current_page, total_pages=total_pages), *args, **kwargs)



        __gather_entities.__name__ = f.__name__
        return __gather_entities
