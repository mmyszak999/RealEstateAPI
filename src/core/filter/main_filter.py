import operator
from distutils.util import strtobool
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, cast, Date
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select

from src.core.exceptions import NoSuchFieldException, UnavailableFilterFieldException


class Filter(Select):
    def __init__(self, model, inst, current_model=None):
        self.main_model = model
        self.inst = inst
        self.current_model = current_model or model
        self.field = None
        self.filter_params = None

    def __lt__(self, other):
        return self._apply_operator(operator.lt, other)

    def __gt__(self, other):
        return self._apply_operator(operator.gt, other)

    def __ge__(self, other):
        return self._apply_operator(operator.ge, other)

    def __le__(self, other):
        return self._apply_operator(operator.le, other)

    def __eq__(self, other):
        values = other.split(",")
        if len(values) > 1:
            values = [self._apply_operator_base(value) for value in values]
            return self.inst.filter(getattr(self.current_model, self.field).in_(values))
        return self._apply_operator(operator.eq, other)

    def __ne__(self, other):
        return self._apply_operator(operator.ne, other)

    def _apply_operator_base(self, other):
        attr_check = getattr(self.current_model, self.field)
        print(attr_check.type, "ww")
        if isinstance(attr_check.type, Boolean):
            other = bool(strtobool(other))
        if isinstance(attr_check.type, Integer):
            other = int(other)
        if isinstance(attr_check.type, Date):
            other = datetime.strptime(other, '%Y-%m-%d').date()
            print(other, "ww")
        else:
            other = cast(other, attr_check.type)
        return other

    def _apply_operator(self, op, other):
        other = self._apply_operator_base(other)
        return self.inst.filter(op(getattr(self.current_model, self.field), other))

    def set_filter_params(self, query_params: list[tuple]) -> None:
        from src.core.utils.filter import filter_query_param_values_extractor

        self.filter_params = filter_query_param_values_extractor(query_params)

    def perform_filter(self, field, operation, value):
        from src.core.utils.filter import FORBIDDEN_FIELDS, get_model_from_key_name

        if len(field.split("__")) == 1:
            self.field = field
            self.current_model = self.main_model

        else:
            key, self.field = field.split("__")
            self.current_model = get_model_from_key_name(self.main_model, key)
            alias = aliased(self.current_model)
            self.inst = self.inst.join(alias, getattr(self.main_model, key))

        if self.field in FORBIDDEN_FIELDS:
            raise UnavailableFilterFieldException

        try:
            inst = getattr(operator, operation)(self, value)
            result = Filter(self.main_model, inst, self.current_model)
            return result
        except AttributeError:
            raise NoSuchFieldException(
                model_name=self.current_model.__name__, field=self.field
            )

    def get_filtered_instances(self):
        for param in self.filter_params:
            self.inst = self.perform_filter(*param).inst
        return self.inst
