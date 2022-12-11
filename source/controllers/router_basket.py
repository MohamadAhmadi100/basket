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
        result["action"] = data.get("action", "add")
        return {"success": True, "data": result, "status_code": 200}
    return {"success": False, "error": "سبد مورد نظر موجود نیست ..", "status_code": 404}


def checkout_check_basket(baskets: dict):
    failed_response = []
    success_response = {}
    for basket_id, cus_baskets in baskets.items():
        try:
            basket_id = int(basket_id)
        except Exception as e:
            return {"success": False, "error": "سبد مورد نظر موجود نیست ...", "status_code": 404}
        if type(success_response.get(f"{basket_id}")) != list:
            success_response[f"{basket_id}"] = []
        if type(cus_baskets) == list:
            for cus_basket in cus_baskets:
                basket = Basket(basket_id=basket_id)
                if not basket.is_salable_basket():
                    failed_response.append({
                        "name": str(basket_id),
                        "status": "failed",
                        "message": f"سبد با شناسه {basket_id} به دلیل اتمام موجودی حذف شد"
                    })
                if result := basket.checkout_products(
                        cus_mandatory_products=cus_basket.get("mandatory_products") or cus_basket.get(
                            "mandatoryProducts"),
                        cus_selective_products=cus_basket.get("selective_products") or cus_basket.get(
                            "selectiveProducts"),
                        cus_optional_products=cus_basket.get("optional_products") or cus_basket.get(
                            "optionalProducts")):
                    if result.get("removed") and len(result.get("removed")):
                        removed = result.get("removed")
                        removed_items = [
                            f'{item.get("name")} از سبد خرید به دلیل عدم تطبیق آدرس با انبار انتخاب شده حذف شد' for item
                            in removed]
                        removed_names = [f'{item.get("name")}' for item in removed]
                        del result["removed"]
                        failed_response.append(
                            {
                                "name": removed_names,
                                "status": "removed",
                                "message": removed_items
                            })
                    success_response[f"{basket_id}"].append(result)
                else:
                    failed_response.append({
                        "name": str(basket_id),
                        "status": "failed",
                        "message": f"سبد با شناسه {basket_id} به دلیل اتمام موجودی حذف شد"
                    })
    if success_response:
        return {"success": True, "result": success_response, "failed": failed_response, "status_code": 200}
    return {"success": False, "error": "سبد مورد نظر موجود نیست ..", "status_code": 404}
