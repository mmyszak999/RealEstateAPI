from copy import copy

PAGINATION_PARAMS_HEADERS = ["page", "size"]
SORT_PARAMS_HEADER = "sort"
FORBIDDEN_FIELDS = [
    "id",
    "password",
    "user_id",
    "stock_user_history",
    "rack_level_id",
    "rack_id",
    "section_id",
    "warehouse_id",
    "stock_id",
    "rack_level_slot_id",
    "waiting_room_id",
    "reception_id",
    "product_id",
    "is_superuser",
    "has_password_set",
]

PAGINATION_PARAMS_HEADERS_COPY = copy(PAGINATION_PARAMS_HEADERS)
PARAM_HEADERS_WITHOUT_FILTERS = PAGINATION_PARAMS_HEADERS_COPY + [SORT_PARAMS_HEADER]
