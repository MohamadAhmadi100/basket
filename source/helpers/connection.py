import pymongo
from config import config


class MongoConnection:
    __slots__ = ["__client", "__db_name", "collection", "__instance", "__db_name_log", "__db_name_counter"]

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(MongoConnection, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__client = pymongo.MongoClient(
            config.MONGO_HOST,
            config.MONGO_PORT,
            username=config.MONGO_USER,
            password=config.MONGO_PASS
        )
        self.__db_name = self.__client["db-basket"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__client.close()

    @property
    def basket(self):
        return self.__db_name["basket"]

    @property
    def log(self):
        return self.__db_name["basket"].log

    @property
    def counter(self):
        return self.__db_name["db-basket"].counter

