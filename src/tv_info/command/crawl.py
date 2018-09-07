from logging import getLogger

from tv_info.yahoo_tv.crawler import YahooTVCrawler
from ..config import Config

logger = getLogger(__name__)


def start(config: Config):
    logger.info("start crawl")
    CrawlCommand(config).start()


class CrawlCommand:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        crawler = YahooTVCrawler(self.config)
        crawler.start()
