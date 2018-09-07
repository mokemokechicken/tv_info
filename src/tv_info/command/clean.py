from logging import getLogger

from ..config import Config

logger = getLogger(__name__)


def start(config: Config):
    logger.info("start hello")
    HelloCommand(config).start()


class HelloCommand:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        pass