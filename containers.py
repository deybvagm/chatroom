from dependency_injector import providers, containers

from rabbitmq.pubsub import RabbitmqClient
from handlers.chat_participant import ChatParticipant
from handlers.bot_handler import BotHandler
from handlers.auth import AuthHandler
from handlers.storage import Storage
from db.db_connector import DBConnector


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    rabbitmq_client = providers.Factory(
        RabbitmqClient,
        conf=config.rabbitmq
    )

    db_connector = providers.Singleton(
        DBConnector,
        config=config.db
    )

    storage = providers.Singleton(
        Storage,
        db_connector=db_connector
    )
    chat_participant = providers.Factory(
        ChatParticipant,
        message_broker=rabbitmq_client,
        config=config,
        storage=storage
    )

    bot_handler = providers.Factory(
        BotHandler,
        config=config,
        message_broker=rabbitmq_client
    )

    auth_handler = providers.Singleton(
        AuthHandler,
        store_handler=storage
    )


