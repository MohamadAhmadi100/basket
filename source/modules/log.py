import time
from datetime import datetime

from source.helpers.connection import MongoConnection
from source.modules.date_convertor import jalali_datetime


def save_create_log(basket_name: str, staff_id: int = 20000) -> bool:
    pipeline = {
        "basketName": basket_name,
        "staffId": staff_id,
        "action": "createBasket",
        "customerActionTime": time.time(),
        "customerJalaliActionTime": jalali_datetime(datetime.now())
    }
    with MongoConnection() as mongo:
        result = mongo.log.insert_one(pipeline)
    return bool(result.acknowledged)
