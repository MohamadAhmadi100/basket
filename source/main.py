from source.broker.listener import callback
from config import config
from source.broker.rabbitmq_client import RabbitRPCClient

if __name__ == '__main__':
    rpc = RabbitRPCClient(
        receiving_queue=f"{config.APP_NAME}_googooli",
        callback=callback,
        exchange_name="headers_exchange",
        headers={config.APP_NAME: True},
        headers_match_all=True
    )
