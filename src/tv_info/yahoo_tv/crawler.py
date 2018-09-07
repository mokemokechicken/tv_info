import re
from collections import namedtuple
from copy import copy
from dataclasses import dataclass
from logging import getLogger
from os.path import exists
from time import sleep
from typing import List, Iterable
from urllib.parse import ParseResult, parse_qsl
from urllib.parse import parse_qs, urlparse
from urllib.parse import urlencode

from selenium import webdriver

from tv_info.config import Config
from tv_info.lib.file_util import load_json_from_file, save_json_to_file
from tv_info.lib.mecab_parser import MecabParser
from tv_info.lib.web_browser import WebBrowser

logger = getLogger(__name__)


class YahooTVCrawler:
    def __init__(self, config: Config):
        self.config = config
        self.parser = None  # type: MecabParser
        self.omit_words = set(self.config.data.omit_words)

    def start(self):
        # self.bs = soup = BeautifulSoup(html, "html.parser")
        self.parser = MecabParser(self.config.resource.mecab_dict_path)
        for top_url in self.config.data.top_url_list:
            with WebBrowser() as driver:
                self.start_crawl(driver, top_url)

    def start_crawl(self, driver: webdriver.Chrome, top_url: str):
        """

        :param driver:
        :param top_url:
        :return:

        1. まず、以下のようなリンクを探す。翌日以降のリンクがあるっぽい。
        https://tv.yahoo.co.jp/listings/23/?&st=9&s=1&va=6&vb=1&vc=0&vd=0&ve=1&d=20180908

        2. va=24 にすると24時間分みれるので、そこを書き換えてアクセスする

        3. https://tv.yahoo.co.jp/program/48608517/ のようなリンクが番組詳細なので、さらに進む

        4. 番組情報を取り出して、保存する
        """
        logger.info(f"start crawling from {top_url}")
        list_info = self.load_program_list()
        if top_url not in list_info:
            driver.get(top_url)
            sleep(1)
            links = self.find_and_make_daily_program_list_link(driver, top_url)
            program_urls = self.collect_program_urls(driver, links)
            list_info[top_url] = program_urls
            save_json_to_file(self.config.resource.tv_program_list_path, list_info)
        else:
            logger.info("skip crawling program list")
            program_urls = list_info[top_url]

        self.collect_program_details(driver, program_urls)

    def collect_program_details(self, driver: webdriver.Chrome, program_urls: List[dict]):
        detail_info = self.load_program_detail()
        date_regex = re.compile("年.+月.+日")
        for ui in program_urls:
            if ui["url"] in detail_info:
                continue
            logger.debug(f"fetching {ui['url']}")
            driver.get(ui['url'])
            sleep(1)
            # $("div#main h2 b")
            # $("div#main h3 ~ p")
            # $("div#main *[itemprop]")
            # $('div#main p[class*="clearfix"] em')
            selectors = [
                "div#main h2 b",
                "div#main h3 ~ p",
                "div#main *[itemprop]",
                'div#main p[class~="clearfix"] em',
            ]

            text_set = set()
            for sel in selectors:
                for el in driver.find_elements_by_css_selector(sel):
                    if not date_regex.search(el.text):
                        text_set.add(el.text)
            logger.debug(text_set)
            keywords = self.extract_keywords(text_set)
            pg_info = {
                "day": ui['day'],
                "texts": list(text_set),
                "keywords": keywords,
            }
            detail_info[ui['url']] = pg_info
            save_json_to_file(self.config.resource.tv_program_detail_path, detail_info)

    def extract_keywords(self, text_set: Iterable[str]) -> List[str]:
        keywords = set()
        for text in text_set:
            words = self.parser.parse(text)
            for word, info in words:
                if word not in self.omit_words and info[0] == "名詞" and info[1] in ('固有名詞', ):
                    keywords.add(word)
        return list(sorted(keywords))

    @staticmethod
    def find_and_make_daily_program_list_link(driver: webdriver.Chrome, top_url):
        logger.info("find_and_make_daily_program_list_link")
        links = []
        first_link_sample = None  # type: ParseResult
        days = set()

        for elem in driver.find_elements_by_tag_name('a'):
            link = elem.get_attribute("href")
            if link and top_url in link:
                # qs = {'st': ['9'], 's': ['1'], 'va': ['6'], 'vb': ['1'], 'vc': ['0'], 'vd': ['0'],
                # 've': ['1'], 'd': ['20180908']}
                qs = parse_qs(link)
                if "d" in qs and not first_link_sample:
                    first_link_sample = urlparse(link)
                if qs.get("d"):
                    days.add(qs["d"][0])

        for day in sorted(days):
            qs = []
            for k, v in parse_qsl(first_link_sample.query):
                if k == "va":
                    qs.append((k, 24))
                elif k == 'd':
                    qs.append((k, day))
                else:
                    qs.append((k, v))
            s = copy(first_link_sample)
            link = f"{s.scheme}://{s.netloc}{s.path}?{urlencode(qs)}"
            logger.debug(f"List URL: {link}")
            links.append(dict(day=day, url=link))

        return links

    @staticmethod
    def collect_program_urls(driver: webdriver.Chrome, links: List[dict]):
        logger.info("collect_program_urls")
        program_urls = {}
        for li in links:
            driver.get(li['url'])
            sleep(1)
            for elem in driver.find_elements_by_tag_name("a"):
                link = elem.get_attribute("href")
                if link and '//tv.yahoo.co.jp/program/' in link:
                    link = link.split("?")[0]
                    program_urls[link] = dict(day=li["day"], url=link)
                    logger.debug(f"Program URL: {link}")
        return list(program_urls.values())

    def load_program_list(self):
        if exists(self.config.resource.tv_program_list_path):
            return load_json_from_file(self.config.resource.tv_program_list_path)
        else:
            return {}

    def load_program_detail(self):
        if exists(self.config.resource.tv_program_detail_path):
            return load_json_from_file(self.config.resource.tv_program_detail_path)
        else:
            return {}
