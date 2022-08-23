import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME: str = os.getenv("APP_NAME")

    MONGO_USER: str = os.getenv("MONGO_USER")
    MONGO_PASS: str = os.getenv("MONGO_PASS")
    MONGO_HOST: str = os.getenv("MONGO_HOST")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT"))
    MONGO_DB: str = os.getenv("MONGO_DB")
    BASKET_COLLECTION: str = os.getenv("BASKET_COLLECTION")

    RABBIT_HOST: str = os.getenv("RABBIT_HOST")
    RABBIT_PORT: str = int(os.getenv("RABBIT_PORT"))
    RABBIT_USER: str = os.getenv("RABBIT_USER")
    RABBIT_PASSWORD: str = os.getenv("RABBIT_PASSWORD")


config = Config()
