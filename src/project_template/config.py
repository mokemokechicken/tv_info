import os
from pathlib import Path

from moke_config import ConfigBase


def _system_dir():
    return Path(__file__).parent.parent.parent


class Config(ConfigBase):
    def __init__(self):
        self.runtime = RuntimeConfig()
        self.resource = ResourceConfig(self)
        self.data = DataConfig()


class RuntimeConfig(ConfigBase):
    def __init__(self):
        self.args = None


class ResourceConfig(ConfigBase):
    def __init__(self, config: Config):
        self._config = config
        self.system_dir = _system_dir()

        # Log
        self.log_dir = self.system_dir / "log"
        self.tensorboard_dir = self.log_dir / "tensorboard"
        self.main_log_path = self.log_dir / "main.log"
        self.resource_dir = self.system_dir / "resource"

    @property
    def working_dir(self):
        return f"{self.system_dir}/working"

    def create_base_dirs(self):
        dirs = [self.log_dir, self.working_dir]

        for d in dirs:
            os.makedirs(d, exist_ok=True)


class DataConfig(ConfigBase):
    def __init__(self):
        pass
