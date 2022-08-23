from source.models.basket import Basket
from source.modules import log


def create_basket(basket_name: str, warehouse_id: str, staff_id: int = 20000):
    basket = Basket(basket_name, warehouse_id)
    if basket.is_basket_exists:
        return {"success": False, "error": "نام سبد تکراری است", "status_code": 422}
    basket.set_data()
    if basket.save():
        log.save_create_log(basket_name=basket_name, staff_id=staff_id)
        return {"success": True, "message": "سید با موفقیت ایجاد شد", "status_code": 201}
    return {"success": False, "error": "مشکلی رخ داد. لطفا مجددا تلاش کنید", "status_code": 417}

