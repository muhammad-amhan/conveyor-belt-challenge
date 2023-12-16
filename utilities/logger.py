import logging


class Logger:
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)

    def configure_logging(self, debug: bool):
        verbose = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=verbose,
            format='%(asctime)s %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
        )
        return self.logger

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

