import json
from source.models.basket import Basket
from source.modules import log
from source.modules.setter import Filter
from source.modules.getter import GetData


def create_basket(basket_name: str, storage_id: str, staff_user_id: int = 20000):
    basket = Basket(basket_name=basket_name, storage_id=storage_id)
    # if basket.is_basket_name_exists():
    #     return {"success": False, "error": "نام سبد تکراری است", "status_code": 422}
    if basket_id := basket.save():
        log.save_create_log(basket_name=basket_name, staff_id=staff_user_id)
        return {"success": True, "message": "سید با موفقیت ایجاد شد", "data": {"basketId": basket_id},
                "status_code": 201}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 417}


def add_product_to_basket(basket_id: int, product_type: str, system_code: str, quantity: int, storage_id: str,
                          basket_price: int, min_quantity: int, max_quantity: int, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.check_storage(storage_id=storage_id):
        return {"success": False, "error": "انبار انتخاب شده با انبار سبد یکسان نیست", "status_code": 422}
    if not basket.is_exists_product(system_code):
        if basket.add_product_to_basket(system_code=system_code, product_type=product_type, quantity=quantity,
                                        price=basket_price, min_quantity=min_quantity, max_quantity=max_quantity):
            price = basket.get_price()
            return {"success": True, "message": {"message": "محصول با موفقیت اضافه شد", "data": price},
                    "status_code": 202}
        else:
            return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 417}
    return {"success": False, "error": "محصول در سبد موجود است", "status_code": 422}


def set_selective_quantity_products(basket_id: int, min_products_quantity: int, max_products_quantity: int,
                                    staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if basket.set_selective_quantity(min_quantity=min_products_quantity, max_quantity=max_products_quantity):
        return {"success": True, "message": "اطلاعات با موفقیت ثبت شد", "status_code": 202}
    return {"success": False, "error": "محصول انتخابی در سبد موجود نیست", "status_code": 422}


def edit_basket_product(basket_id: int, system_code: str, quantity: int, storage_id: str, basket_price: int,
                        min_quantity: int, max_quantity: int, product_type: str, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.check_storage(storage_id=storage_id):
        return {"success": False, "error": "انبار انتخاب شده با انبار سبد یکسان نیست", "status_code": 422}
    if not basket.is_exists_product(system_code):
        return {"success": False, "error": "محصول در سبد موجود نیست", "status_code": 404}
    if basket.edit_product(system_code=system_code, quantity=quantity, price=basket_price, min_quantity=min_quantity,
                           max_quantity=max_quantity):
        price = basket.get_price()
        if product_type == "selective":
            basket.change_basket_status_selective()
            return {"success": True,
                    "message": {"message": "محصول با موفقیت به روز شد. لطفا مجددا سبد را تکمیل و فعال کنید",
                                "data": price},
                    "status_code": 200}
        return {"success": True, "message": {"message": "محصول با موفقیت به روز شد", "data": price}, "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def delete_basket_product(basket_id: int, system_code: str, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.is_exists_product(system_code):
        return {"success": False, "error": "محصول در سبد موجود نیست", "status_code": 404}
    if basket.delete_product(system_code=system_code):
        price = basket.get_price()
        return {"success": True, "message": {"message": "محصول با موفقیت حذف شد", "data": price}, "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def complete_basket(basket_id: int, basket_start_date: str, basket_end_date: str, sales_per_day: int, sales_number: int,
                    basket_status: str, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.is_valid_basket(basket_end_date=basket_end_date):
        return {"success": False, "error": "سبد مورد نظر امکان تکمیل ندارد. لطفا مجددا اطلاعات را بررسی و ویرایش کنید",
                "status_code": 404}
    if basket.complete(basket_start_date=basket_start_date, basket_end_date=basket_end_date,
                       sales_per_day=sales_per_day, sales_number=sales_number, basket_status=basket_status):
        price = basket.get_price()
        return {"success": True, "message": {"message": "وضعیت سبد با موفقیت به تکمیل شده تغییر کرد", "data": price},
                "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def delete_basket(basket_id: int, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if basket.delete():
        return {"success": True, "message": "سبد با موفقیت حذف شد", "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def activate_basket(basket_id: int, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if basket.activate():
        return {"success": True, "message": "سبد با موفقیت فعال شد", "status_code": 200}
    return {"success": False, "error": "ناموفق. لطفا اطلاعات سبد را مجددا بررسی و ویرایش کنید", "status_code": 422}


def deactivate_basket(basket_id: int, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if basket.deactivate():
        return {"success": True, "message": "سبد با موفقیت غیرفعال شد", "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def get_all_available_baskets_crm(data: str = None):
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
            sort_type = "desc"
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


def get_basket_by_id(basket_id: int):
    basket = Basket(basket_id=basket_id)
    if basket.is_basket_exists():
        if not basket.is_complete_basket():
            return {"success": False, "error": "برای ویرایش سبد ابتدا اطلاعات سبد را کامل کنید", "status_code": 404}
        price = basket.get_price()
        return {"success": True, "message": dict(basket.get_basket(), **price), "status_code": 200}
    return {"success": False, "error": "سبد مورد نظر موجود نیست ", "status_code": 404}
