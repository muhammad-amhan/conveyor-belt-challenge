import logging


class Logger:
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)

    def configure_logging(self, debug: bool):
        verbose = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=verbose)
        return self.logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

