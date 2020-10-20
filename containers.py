from dependency_injector import providers, containers

from rabbitmq.pubsub import RabbitmqClient
from handlers.chat_participant import ChatParticipant
from handlers.bot_handler import BotHandler
from handlers.auth import AuthHandler
from db.db_connector import DBConnector


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    rabbitmq_client = providers.Factory(
        RabbitmqClient,
        conf=config.rabbitmq
    )
    chat_participant = providers.Factory(
        ChatParticipant,
        message_broker=rabbitmq_client,
        config=config
    )

    bot_handler = providers.Factory(
        BotHandler,
        config=config,
        message_broker=rabbitmq_client
    )

    db_connector = providers.Singleton(
        DBConnector,
        config=config.db
    )

    auth_handler = providers.Singleton(
        AuthHandler,
        store_handler=db_connector
    )
