from containers import Container

if __name__ == "__main__":
    container = Container()
    container.config.from_yaml('config/config_bot.yml')
    bot = container.bot_handler()
    bot.start()
