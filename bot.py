from dependency_injector.wiring import Provide
from containers import Container


def run_bot(bot_handler=Provide[Container.bot_handler]):
    bot_handler.start()


if __name__ == "__main__":
    container = Container()
    container.config.from_yaml('config_bot.yml')
    bot = container.bot_handler()
    bot.start()
