import json
from source.models.basket import Basket
from source.modules import log
from source.modules.setter import Filter
from source.modules.getter import GetData


def get_all_available_baskets(data: str = None):
    try:
        data = {} if data is None else json.loads(data)
        records = Filter()
        period_filters: dict = {}
        value_filters: dict = {}
        search_query: dict = {}
        if filters := data.get("filters"):
            period_filters: dict = records.set_period_filters(filters) or {}
            value_filters: dict = records.set_value_filters(filters) or {}
        if search_phrase := data.get("search"):
            search_query = records.set_search_query(search_phrase)
        filters = dict(period_filters, **value_filters, **search_query)
        if not data.get("sortType"):
            sort_type = "asc"
        else:
            sort_type = "asc" if data.get("sortType") == "ascend" else "desc"
        sort_name = data.get("sortName") or "basketId"
        return GetData().executor(
            queries=filters,
            number_of_records=data.get("perPage") or "15",
            page=data.get("page") or "1",
            sort_name=sort_name,
            sort_type=sort_type or "asc"
        )
    except Exception as e:
        return {"success": False, "error": e, "status_code": 404}


def check_basket_is_valid(data: str):
    data = json.loads(data)
    basket = Basket(basket_id=data.get("basket_id"))
    if not basket.is_salable_basket():
        return {"success": False, "message": "سبد مورد نظر موجود نیست", "status_code": 404}
    if result := basket.check_products(cus_mandatory_products=data.get("mandatory_products"),
                                       cus_selective_products=data.get("selective_products"),
                                       cus_optional_products=data.get("optional_products")):
        return {"success": True, "data": result, "status_code": 200}
    return {"success": False, "error": "سبد مورد نظر موجود نیست ..", "status_code": 404}
