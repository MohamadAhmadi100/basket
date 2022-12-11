VALID_PERIOD_FILTERS = ["basketJalaliCreateTime", "basketJalaliStartDate", "basketJalaliEndDate"]
VALID_VALUE_FILTERS = ["basketStatus", "storageId"]
VALID_SEARCH_FIELDS = ["basketId", "basketName"]


class Filter:
    def __init__(self):
        self.valid_period_filters: list = VALID_PERIOD_FILTERS or []
        self.valid_value_filters: list = VALID_VALUE_FILTERS or []
        self.valid_search_fields: list = VALID_SEARCH_FIELDS or []
        self.period_filters: dict = {}
        self.value_filters: dict = {}

    def set_period_filters(self, periods: dict) -> dict:
        self.period_filters = {filter_: value for filter_, value in periods.items() if
                               filter_ in self.valid_period_filters and value and type(value) == dict}
        period = {}
        for filter_, value in self.period_filters.items():
            if value.get("start") and value.get("end"):
                value["$gt"] = value.get("start")
                value["$lt"] = value.get("end")
                del value["start"]
                del value["end"]
            elif value.get("start"):
                value["$lt"] = value.get("start")
                del value["start"]
            elif value.get("end"):
                value["$gt"] = value.get("end")
                del value["end"]
            else:
                continue
            period[filter_] = value
        return period

    def set_value_filters(self, values: dict) -> dict:
        self.value_filters = {filter_: {"$in": value} for filter_, value in values.items() if
                              filter_ in self.valid_value_filters and value and type(value) == list}

        return self.value_filters

    def set_search_query(self, search_phrase):
        search_list = [{search_field: {"$regex": search_phrase}} for search_field in self.valid_search_fields]
        return {"$or": search_list} if search_list else {}
