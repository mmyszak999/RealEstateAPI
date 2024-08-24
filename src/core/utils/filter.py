from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import RelationshipProperty

from src.core.filter.main_filter import Filter
from src.core.utils.constants import (
    FORBIDDEN_FIELDS,
    PAGINATION_PARAMS_HEADERS,
    PARAM_HEADERS_WITHOUT_FILTERS,
    SORT_PARAMS_HEADER,
)
from src.core.utils.sort import sort_instances
from src.database.db_connection import Base


def filter_query_param_values_extractor(params_list: list[str]):
    desired_params_list = [
        param for param in params_list if param[0] not in PARAM_HEADERS_WITHOUT_FILTERS
    ]
    for param in desired_params_list:
        key, value = param
        try:
            field, oper = key.rsplit("__", 1)
        except Exception:
            field = key
            oper = "eq"
        yield field, oper, value


def filter_instances(query_params: list[tuple], instances, model):
    filter_class = Filter(model, instances)
    filter_class.set_filter_params(query_params)
    filter_class.get_filtered_instances()
    return filter_class.inst


def filter_and_sort_instances(query_params: list[tuple], instances, model):
    params_keys = [param[0] for param in query_params]
    pagination_keys = [
        param for param in params_keys if param in PAGINATION_PARAMS_HEADERS
    ]
    if pagination_keys == params_keys:
        return instances

    [params_keys.remove(value) for value in pagination_keys]
    check_if_sort_key = SORT_PARAMS_HEADER in params_keys
    filter_keys = [param for param in params_keys if param != SORT_PARAMS_HEADER]
    if filter_keys:
        instances = filter_instances(query_params, instances, model)

    if check_if_sort_key:
        instances = sort_instances(query_params, instances, model)

    return instances


def get_model_from_key_name(model, relationship_key: str):
    mapper = class_mapper(model)
    for property in mapper.iterate_properties:
        if (
            isinstance(property, RelationshipProperty)
            and property.key == relationship_key
        ):
            for klass in Base.__subclasses__():
                if klass.__tablename__ == property.target.name:
                    return klass
