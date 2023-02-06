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
                return bool(result and result.get("basketStatus") != "archive")
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

    def check_storage(self, storage_id: str):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            result = mongo.basket.find_one(query_operator, projection_operator)
            if result.get("storageId") == storage_id:
                return True
        return False

    def set_selective_quantity(self, min_quantity: int, max_quantity: int):
        query_operator = {"basketId": self.basket_id}
        modify_operator = {
            "$set": {
                "minSelectiveProductsQuantity": min_quantity,
                "maxSelectiveProductsQuantity": max_quantity,
            }
        }
        with MongoConnection() as mongo:
            result = mongo.basket.find_one(query_operator, {"_id": 0})
            if not result.get("selectiveProducts") or not len(result.get("selectiveProducts")):
                return False
            if result := mongo.basket.update_one(
                    query_operator,
                    modify_operator,
            ):
                return bool(result.acknowledged)
        return

    def add_product_to_basket(self, system_code: str, product_type: str, quantity: int, min_quantity: int,
                              max_quantity: int, price: int):

        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            basket = mongo.basket.find_one(query_operator, projection_operator)
            if product_type == "mandatory":
                body = {
                    "systemCode": system_code,
                    "quantity": quantity,
                    "basketPrice": price,
                    "storageId": basket.get("storageId"),
                }
            else:
                body = {
                    "systemCode": system_code,
                    "minQuantity": min_quantity,
                    "maxQuantity": max_quantity,
                    "basketPrice": price,
                    "storageId": basket.get("storageId"),
                }
            push_operator = {
                "$push":
                    {
                        f"{product_type}Products": body
                    }
            }
            result = mongo.basket.update_one(query_operator, push_operator, upsert=True)
        return bool(result.acknowledged)

    def edit_product(self, system_code: str, quantity: int, price: int, min_quantity: int, max_quantity: int):
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
                    f"{product_type}.$[elem].minQuantity": min_quantity,
                    f"{product_type}.$[elem].maxQuantity": max_quantity,
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

    def is_valid_basket(self, basket_end_date):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                result = mongo.basket.find_one(query_operator, projection_operator)
                return bool(result.get("basketStatus") in ["pend", "complete", "active"] and len(
                    result.get("mandatoryProducts")) and basket_end_date >= jalali_datetime(
                    datetime.now()))
            except Exception:
                return False

    def complete(self, basket_start_date: str, basket_end_date: str, sales_per_day: int, sales_number: int,
                 basket_status: str):
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

    def get_price(self):
        query_operator = {"basketId": self.basket_id}
        with MongoConnection() as mongo:
            result = mongo.basket.aggregate(
                [
                    {
                        "$match": query_operator,
                    },
                    {
                        "$project": {
                            "mandatoryPrice": {
                                '$reduce': {
                                    'input': "$mandatoryProducts",
                                    'initialValue': 0,
                                    'in': {
                                        "$add": ["$$value", {"$multiply": ["$$this.quantity", '$$this.basketPrice']}]
                                    }
                                }
                            },
                            "selectiveMinPrice": {
                                '$reduce': {
                                    'input': "$selectiveProducts",
                                    'initialValue': 0,
                                    'in': {
                                        "$add": ["$$value", {"$multiply": ["$$this.minQuantity", '$$this.basketPrice']}]
                                    }
                                }
                            },
                            "optionalMinPrice": {
                                '$reduce': {
                                    'input': "$optionalProducts",
                                    'initialValue': 0,
                                    'in': {
                                        "$add": ["$$value", {"$multiply": ["$$this.minQuantity", '$$this.basketPrice']}]
                                    }
                                }
                            },
                            "selectiveMaxPrice": {
                                '$reduce': {
                                    'input': "$selectiveProducts",
                                    'initialValue': 0,
                                    'in': {
                                        "$add": ["$$value", {"$multiply": ["$$this.maxQuantity", '$$this.basketPrice']}]
                                    }
                                }
                            },
                            "optionalMaxPrice": {
                                '$reduce': {
                                    'input': "$optionalProducts",
                                    'initialValue': 0,
                                    'in': {
                                        "$add": ["$$value", {"$multiply": ["$$this.maxQuantity", '$$this.basketPrice']}]
                                    }
                                }
                            },
                        }
                    },
                    {
                        "$project": {
                            "minBasketPrice": {
                                "$add": ["$mandatoryPrice", "$selectiveMinPrice"]
                            },
                            "maxBasketPrice": {
                                "$add": ["$mandatoryPrice", "$selectiveMaxPrice"]
                            },
                            "mandatoryPrice": 1,
                            "selectiveMinPrice": 1,
                            "optionalMinPrice": 1,
                            "selectiveMaxPrice": 1,
                            "optionalMaxPrice": 1,
                            "_id": 0
                        }
                    }
                ]
            )
            return list(result)[0] or None

    def get_basket(self):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                return mongo.basket.find_one(query_operator, projection_operator)
            except Exception:
                return False

    def is_salable_basket(self):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                result = mongo.basket.find_one(query_operator, projection_operator)
                return bool(
                    result.get("basketStatus") == "active" and len(result.get("mandatoryProducts")) and result.get(
                        "basketJalaliEndDate") >= jalali_datetime(datetime.now()))
            except Exception:
                return False

    def check_products(self, cus_mandatory_products: list, cus_selective_products: list, cus_optional_products: list):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                result = mongo.basket.find_one(query_operator, projection_operator)
            except Exception:
                return False
        if len(result.get("mandatoryProducts")) != len(cus_mandatory_products):
            return False
        if result.get("minSelectiveProductsQuantity") and result.get("maxSelectiveProductsQuantity") and (
                len(cus_selective_products) < result.get("minSelectiveProductsQuantity") or len(
            cus_selective_products) > result.get("maxSelectiveProductsQuantity")):
            return False
        for mandatory_product in result.get("mandatoryProducts"):
            for cus_mandatory_product in cus_mandatory_products:
                if mandatory_product.get("systemCode") == cus_mandatory_product.get("systemCode"):
                    if mandatory_product.get("quantity") != cus_mandatory_product.get("quantity"):
                        return False
                    cus_mandatory_product["basketPrice"] = mandatory_product.get("basketPrice")
        for cus_selective_product in cus_selective_products:
            flag = False
            for selective_product in result.get("selectiveProducts"):
                if selective_product.get("systemCode") == cus_selective_product.get("systemCode"):
                    flag = True
                    if (cus_selective_product.get("quantity") < selective_product.get(
                            "minQuantity") or cus_selective_product.get("quantity") > selective_product.get(
                        "maxQuantity")):
                        return False
                    cus_selective_product["basketPrice"] = selective_product.get("basketPrice")
            if not flag:
                return False
            else:
                continue
        if not cus_optional_products:
            return {"basketId": result.get("basketId"), "mandatoryProducts": result.get("mandatoryProducts"),
                    "selectiveProducts": cus_selective_products, "basketSalesNumber": result.get("basketSalesNumber"),
                    "basketSalesPer_day": result.get("basketSalesPerDay"), "storageId": result.get("storageId"),
                    "minSelectiveProductsQuantity": result.get("minSelectiveProductsQuantity"),
                    "basketName": result.get("basketName")}
        removed = []
        for cus_optional_product in cus_optional_products:
            for optional_product in result.get("optionalProducts"):
                if optional_product.get("systemCode") == cus_optional_product.get("systemCode"):
                    if (cus_optional_product.get("quantity") < optional_product.get(
                            "minQuantity") or cus_optional_product.get("quantity") > optional_product.get(
                        "maxQuantity")):
                        removed.append(cus_optional_product)
                    cus_optional_product["basketPrice"] = optional_product.get("basketPrice")
        if len(removed):
            return {"basketId": result.get("basketId"), "mandatoryProducts": result.get("mandatoryProducts"),
                    "selectiveProducts": cus_selective_products, "optionalProducts": cus_optional_products,
                    "basketSalesNumber": result.get("basketSalesNumber"),
                    "basketSalesPer_day": result.get("basketSalesPerDay"), "storageId": result.get("storageId"),
                    "minSelectiveProductsQuantity": result.get("minSelectiveProductsQuantity"), "removed": removed,
                    "basketName": result.get("basketName")}
        return {"basketId": result.get("basketId"), "mandatoryProducts": result.get("mandatoryProducts"),
                "selectiveProducts": cus_selective_products, "optionalProducts": cus_optional_products,
                "basketSalesNumber": result.get("basketSalesNumber"),
                "basketSalesPer_day": result.get("basketSalesPerDay"), "storageId": result.get("storageId"),
                "minSelectiveProductsQuantity": result.get("minSelectiveProductsQuantity"),
                "basketName": result.get("basketName")}

    def checkout_products(self, cus_mandatory_products: list, cus_selective_products: list,
                          cus_optional_products: list):
        query_operator = {"basketId": self.basket_id}
        projection_operator = {"_id": 0}
        with MongoConnection() as mongo:
            try:
                result = mongo.basket.find_one(query_operator, projection_operator)
            except Exception:
                return False
        if len(result.get("mandatoryProducts")) != len(cus_mandatory_products):
            return False
        if result.get("minSelectiveProductsQuantity") and result.get("maxSelectiveProductsQuantity") and (
                len(cus_selective_products) < result.get("minSelectiveProductsQuantity") or len(
                cus_selective_products) > result.get("maxSelectiveProductsQuantity")):
            return False
        for mandatory_product in result.get("mandatoryProducts"):
            for cus_mandatory_product in cus_mandatory_products:
                if mandatory_product.get("systemCode") == cus_mandatory_product.get("systemCode"):
                    if mandatory_product.get("quantity") != cus_mandatory_product.get("count"):
                        return False
                    cus_mandatory_product["price"] = mandatory_product.get("basketPrice")
        for cus_selective_product in cus_selective_products:
            flag = False
            for selective_product in result.get("selectiveProducts"):
                if selective_product.get("systemCode") == cus_selective_product.get("systemCode"):
                    flag = True
                    if (cus_selective_product.get("count") < selective_product.get(
                            "minQuantity") or cus_selective_product.get("count") > selective_product.get(
                        "maxQuantity")):
                        return False
                    cus_selective_product["price"] = selective_product.get("basketPrice")
            if not flag:
                return False
            else:
                continue
        if not cus_optional_products:
            return {"mandatory_products": cus_mandatory_products, "selective_products": cus_selective_products,
                    "optional_products": []}
        new_optional_products = []
        removed = []
        flag = True
        for cus_optional_product in cus_optional_products:
            for optional_product in result.get("optionalProducts"):
                if optional_product.get("systemCode") == cus_optional_product.get("system_code"):
                    if (cus_optional_product.get("quantity") < optional_product.get(
                            "minQuantity") or cus_optional_product.get("count") > optional_product.get(
                        "maxQuantity")):
                        removed.append(cus_optional_product)
                        flag = False
                    cus_optional_product["price"] = optional_product.get("basketPrice")
                if not flag:
                    continue
                new_optional_products.append(cus_optional_product)
        if len(removed):
            return {"mandatory_products": cus_mandatory_products, "selective_products": cus_selective_products,
                    "optional_products": new_optional_products, "removed": removed}
        return {"mandatory_products": cus_mandatory_products, "selective_products": cus_selective_products,
                "optional_products": new_optional_products}
