from src.core.exceptions import NoSuchFieldException, UnavailableSortFieldException
from src.core.utils.constants import FORBIDDEN_FIELDS


class Sort:
    def __init__(self, main_model, inst, current_model=None):
        self.main_model = main_model
        self.inst = inst
        self.current_model = current_model
        self.sort_params = None

    def set_sort_params(self, query_params: list[tuple]) -> None:
        from src.core.utils.sort import sort_query_param_values_extractor

        self.sort_params = sort_query_param_values_extractor(
            query_params, self.current_model
        )

    def get_sorted_instances(self):
        from src.core.utils.filter import get_model_from_key_name

        if self.sort_params:
            for field, sort_order in self.sort_params.items():
                if len(field.split("__")) == 1:
                    self.current_model = self.main_model
                else:
                    key, field = field.split("__")
                    self.current_model = get_model_from_key_name(self.main_model, key)
                if field in FORBIDDEN_FIELDS:
                    raise UnavailableSortFieldException
                try:
                    field = getattr(self.current_model, field)
                    statement = field.asc() if sort_order == "asc" else field.desc()
                    self.inst = self.inst.order_by(statement)
                except AttributeError:
                    raise NoSuchFieldException(
                        model_name=self.current_model.__name__, field=field
                    )
        return self.inst
