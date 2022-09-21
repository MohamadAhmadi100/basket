from source.models.basket import Basket
from source.modules import log


def create_basket(basket_name: str, storage_id: str, staff_user_id: int = 20000):
    basket = Basket(basket_name=basket_name, storage_id=storage_id)
    if basket.is_basket_name_exists():
        return {"success": False, "error": "نام سبد تکراری است", "status_code": 422}
    if basket_id := basket.save():
        log.save_create_log(basket_name=basket_name, staff_id=staff_user_id)
        return {"success": True, "message": "سید با موفقیت ایجاد شد", "data": {"basketId": basket_id},
                "status_code": 201}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 417}


def add_product_to_basket(basket_id: int, product_type: str, system_code: str, quantity: int, basket_price: int,
                          staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.is_exists_product(system_code):
        return {"success": True, "message": "محصول با موفقیت اضافه شد", "status_code": 202} \
            if basket.add_product_to_basket(system_code=system_code, product_type=product_type, quantity=quantity,
                                            price=basket_price) \
            else {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 417}
    return {"success": False, "error": "محصول در سبد موجود است", "status_code": 422}


def edit_basket_product(basket_id: int, system_code: str, quantity: int, basket_price: int, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.is_exists_product(system_code):
        return {"success": False, "error": "محصول در سبد موجود نیست", "status_code": 404}
    if basket.edit_product(system_code=system_code, quantity=quantity, price=basket_price):
        return {"success": True, "message": "محصول با موفقیت به روز شد", "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def delete_basket_product(basket_id: int, system_code: str, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if not basket.is_exists_product(system_code):
        return {"success": False, "error": "محصول در سبد موجود نیست", "status_code": 404}
    if basket.delete_product(system_code=system_code):
        return {"success": True, "message": "محصول با موفقیت حذف شد", "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def complete_basket(basket_id: int, basket_start_date: str, basket_end_date: str, sales_per_day: int, sales_number: int,
                    basket_status: str, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if basket.complete(basket_start_date=basket_start_date, basket_end_date=basket_end_date,
                       sales_per_day=sales_per_day, sales_number=sales_number, basket_status=basket_status):
        return {"success": True, "message": "وضعیت سبد با موفقیت به تکمیل شده تغییر کرد", "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}


def delete_basket(basket_id: int, staff_user_id: int = 20000):
    basket = Basket(basket_id=basket_id)
    if not basket.is_basket_exists():
        return {"success": False, "error": "سبد مورد نظر موجود نیست", "status_code": 404}
    if basket.delete():
        return {"success": True, "message": "سبد با موفقیت حذف شد", "status_code": 200}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 422}
