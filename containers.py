from dependency_injector import providers, containers

from rabbitmq.pubsub import RabbitmqClient
from handlers.chat_participant import ChatParticipant
from handlers.bot_handler import BotHandler


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    rabbitmq_client = providers.Factory(
        RabbitmqClient,
        conf=config
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
