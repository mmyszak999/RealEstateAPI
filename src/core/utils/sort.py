from typing import Any

from sqlalchemy import Table

from src.core.sort.main_sort import Sort
from src.core.utils.constants import (
    PAGINATION_PARAMS_HEADERS,
    PARAM_HEADERS_WITHOUT_FILTERS,
    SORT_PARAMS_HEADER,
)


def sort_query_param_values_extractor(
    params_list: list[tuple], model_class: Table
) -> dict[Any, str]:
    params = [param for param in params_list if param[0] == SORT_PARAMS_HEADER]
    criteria = dict()
    if params:
        for criterion in params[0][1].split(","):
            field, sorting_order = criterion.rsplit("__", 1)
            criteria[field] = sorting_order
        return criteria


def sort_instances(query_params: list[tuple], instances, model):
    sort_class = Sort(model, instances)
    sort_class.set_sort_params(query_params)
    sort_class.get_sorted_instances()
    return sort_class.inst
