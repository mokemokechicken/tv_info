import os
from datetime import date
from pathlib import Path

from moke_config import ConfigBase


def _system_dir():
    return Path(__file__).parent.parent.parent


class Config(ConfigBase):
    def __init__(self):
        self.runtime = RuntimeConfig()
        self.resource = ResourceConfig(self)
        self.data = DataConfig()
        self.browser = BrowserConfig()


class RuntimeConfig(ConfigBase):
    def __init__(self):
        self.args = None


class ResourceConfig(ConfigBase):
    def __init__(self, config: Config):
        self._config = config
        self.system_dir = _system_dir()
        self._today = date.today().strftime("%Y%m%d")

        # Log
        self.log_dir = self.system_dir / "log"
        self.tensorboard_dir = self.log_dir / "tensorboard"
        self.main_log_path = self.log_dir / "main.log"

        # resource
        self.resource_dir = self.system_dir / "resource"

        # crawl
        self.tv_program_list_name = "program_list.json"
        self.tv_program_detail_name = "program_detail.json"
        self.mecab_dict_path = os.environ['MECAB_DICT_PATH']

    @property
    def tv_program_list_path(self):
        return f"{self.today_dir}/{self.tv_program_list_name}"

    @property
    def tv_program_detail_path(self):
        return f"{self.today_dir}/{self.tv_program_detail_name}"

    @property
    def working_dir(self):
        return f"{self.system_dir}/working"

    @property
    def today_dir(self):
        return f"{self.working_dir}/{self._today}"

    def create_base_dirs(self):
        dirs = [self.log_dir, self.working_dir, self.today_dir]

        for d in dirs:
            os.makedirs(d, exist_ok=True)


class DataConfig(ConfigBase):
    def __init__(self):
        self.top_url_list = None
        self.omit_words = []


class BrowserConfig(ConfigBase):
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/65.0.3325.162 Safari/537.36'
