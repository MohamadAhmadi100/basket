import time
from datetime import datetime

from source.helpers.connection import MongoConnection
from source.modules.date_convertor import jalali_datetime


class Basket:
    def __init__(self, basket_name: str = None, storage_id: str = None, basket_id: int = 0):
        self.basket_name = basket_name
        self.storage_id = storage_id
        self.basket_id: int = basket_id
        self.status: str = "pend"
        self.start_date: str = ""
        self.end_date: str = ""
        self.mandatory_products: list = []
        self.selective_products: list = []
        self.optional_products: list = []

    def get_next_sequence_basket_id(self):
        """
        auto increment id generator for self object
        :return: True if basket is the first obj or correct id has been generated
        """
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                basket_id = mongo.counter.find_one({"type": "basket"}, projection_operator)
                if basket_id is not None:
                    self.basket_id = basket_id.get("basketId") + 1
                    mongo.counter.update_one({"type": "basket"}, {"$set": {"basketId": self.basket_id}})
                    if basket_id.get("basketId") < 40000:
                        mongo.counter.update_one({"type": "basket"}, {"$set": {"basketId": 40000}})
                else:
                    mongo.counter.insert_one({"type": "basket", "basketId": 40000})
                    self.basket_id = 40000
                return True
            except Exception:
                return False

    def is_basket_exists(self) -> bool:
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                result = mongo.basket.find_one(query_operator, projection_operator)
                if not result or result.get("basketStatus") == "archive":
                    return False
                return True
            except Exception:
                return False

    def is_basket_name_exists(self) -> bool:
        query_operator = {"basketName": self.basket_name}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            return bool(mongo.basket.find_one(query_operator, projection_operator))

    def save(self):
        if not self.get_next_sequence_basket_id():
            return False
        basket_data: dict = {
            "basketName": self.basket_name,
            "basketId": self.basket_id,
            "storageId": self.storage_id,
            "basketCreateTime": time.time(),
            "basketJalaliCreateTime": jalali_datetime(datetime.now()),
            "basketStatus": "pend",
            "mandatoryProducts": [],
            "selectiveProducts": [],
            "optionalProducts": []
        }
        with MongoConnection() as mongo:
            result: object = mongo.basket.insert_one(basket_data)
            if result.acknowledged:
                return self.basket_id
        return False

    def is_exists_product(self, system_code: str):
        query_operator = {
            "$and": [
                {"basketId": self.basket_id},
                {"$or": [{"mandatoryProducts.systemCode": system_code},
                         {"selectiveProducts.systemCode": system_code},
                         {"optionalProducts.systemCode": system_code}
                         ]}
            ]}
        with MongoConnection() as mongo:
            return list(mongo.basket.find(query_operator)) or False

    def add_product_to_basket(self, system_code: str, product_type: str, quantity: int, price: int):
        query_operator = {"basketId": self.basket_id}
        push_operator = {
            "$push":
                {
                    f"{product_type}Products":
                        {
                            "systemCode": system_code,
                            "quantity": quantity,
                            "basketPrice": price
                        }
                }
        }
        with MongoConnection() as mongo:
            result = mongo.basket.update_one(query_operator, push_operator, upsert=True)
        return bool(result.acknowledged)

    def edit_product(self, system_code: str, quantity: int, price: int):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        product_type: str = ""
        array_filters = [{"elem.systemCode": system_code}]
        with MongoConnection() as mongo:
            basket = mongo.basket.find_one(query_operator, projection_operator)
            for product in basket.get("mandatoryProducts"):
                if product.get("systemCode") == system_code:
                    product_type = "mandatoryProducts"
            for product in basket.get("selectiveProducts"):
                if product.get("systemCode") == system_code:
                    product_type = "selectiveProducts"
            for product in basket.get("optionalProducts"):
                if product.get("systemCode") == system_code:
                    product_type = "optionalProducts"
            modify_operator = {
                "$set": {
                    f"{product_type}.$[elem].quantity": quantity,
                    f"{product_type}.$[elem].basketPrice": price
                }
            }
            if result := mongo.basket.update_one(
                    query_operator,
                    modify_operator,
                    array_filters=array_filters,
                    upsert=False
            ):
                return bool(result.acknowledged)
        return

    def delete_product(self, system_code: str):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        product_type: str = ""
        with MongoConnection() as mongo:
            basket = mongo.basket.find_one(query_operator, projection_operator)
            for product in basket.get("mandatoryProducts"):
                if product.get("systemCode") == system_code:
                    product_type = "mandatoryProducts"
            for product in basket.get("selectiveProducts"):
                if product.get("systemCode") == system_code:
                    product_type = "selectiveProducts"
            for product in basket.get("optionalProducts"):
                if product.get("systemCode") == system_code:
                    product_type = "optionalProducts"
            modify_operator = {
                "$pull": {
                    f"{product_type}": {"systemCode": system_code}
                }
            }
            if result := mongo.basket.update_one(
                    query_operator,
                    modify_operator,
            ):
                return bool(result.acknowledged)
        return

    def complete(self, basket_start_date: str, basket_end_date: str, sales_per_day: int, sales_number: int,
                 basket_status: int):
        query_operator = {"basketId": self.basket_id}
        modify_operator = {
            "$set": {
                "basketJalaliStartDate": basket_start_date,
                "basketJalaliEndDate": basket_end_date,
                "basketSalesPerDay": sales_per_day,
                "basketSalesNumber": sales_number,
                "basketStatus": basket_status,
                "basketJalaliCompleteTime": jalali_datetime(datetime.now()),
            }
        }
        with MongoConnection() as mongo:
            if result := mongo.basket.update_one(
                    query_operator,
                    modify_operator,
            ):
                return bool(result.acknowledged)
        return

    def delete(self):
        query_operator = {"basketId": self.basket_id}
        modify_operator = {
            "$set": {
                "basketStatus": "archive",
                "basketJalaliDeleteTime": jalali_datetime(datetime.now()),
            }
        }
        with MongoConnection() as mongo:
            if result := mongo.basket.update_one(
                    query_operator,
                    modify_operator,
            ):
                return bool(result.acknowledged)
        return
