import time
from datetime import datetime
import pymongo.errors
import requests
from config import config
from source.helpers.connection import MongoConnection
from source.modules.date_convertor import jalali_datetime


class Basket:
    def __init__(self, basket_name: str = None, warehouse_id: str = None, basket_id: int = 0):
        self.basket_name = basket_name
        self.warehouse_id = warehouse_id
        self.basket_id: int = basket_id
        self.status: str = "pend"
        self.start_date: str = ""
        self.end_date: str = ""
        self.basket_name: str = basket_name
        self.products: list = []

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
                    mongo.counter.update_one({"type": "customer"}, {"$set": {"basketId": self.basket_id}})
                    if basket_id.get("basketId") < 40000:
                        mongo.counter.update_one({"type": "basket"}, {"$set": {"basketId": 40000}})
                else:
                    mongo.counter.insert_one({"type": "basket", "basketId": 40000})
                    self.basket_id = 40000
                return True
            except Exception:
                return False

    def is_basket_exists(self) -> bool:
        query_operator = {"basketName": self.basket_name}
        with MongoConnection() as mongo:
            mongo.basket.find_one(query_operator)

    def save(self):
        if not self.get_next_sequence_basket_id():
            return False
        basket_data: dict = {
            "basketId": self.basket_id,
            "warehouseId": self.warehouse_id,
            "basketCreateTime": time.time(),
            "basketJalaliCreateTime": jalali_datetime(datetime.now()),
            "basketStatus": jalali_datetime(datetime.now()),
            "status": "pend"
        }
        with MongoConnection() as mongo:
            result: object = mongo.basket.insert_one(basket_data)
        return bool(result.acknowledged)
