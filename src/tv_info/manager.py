import argparse
from logging import getLogger
import importlib
from os.path import dirname

from moke_config import create_config

from .lib.file_util import load_yaml_from_file
from .config import Config
from .lib.logger import setup_logger

logger = getLogger(__name__)
ROOT_PATH = dirname(dirname(dirname(__file__)))


def create_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()

    def add_common_options(p):
        p.add_argument("--log-level", help="specify Log Level(debug/info/warning/error): default=info",
                       choices=['debug', 'info', 'warning', 'error'])
        p.add_argument("--config", help="specify config file")

    sub_parser = sub.add_parser("hello")
    sub_parser.set_defaults(command='hello')
    add_common_options(sub_parser)

    sub_parser = sub.add_parser("crawl")
    sub_parser.set_defaults(command='crawl')
    add_common_options(sub_parser)
    return parser


def setup(config: Config, args):
    config.resource.create_base_dirs()
    setup_logger(config.resource.main_log_path, level=args.log_level or 'info')
    config.runtime.args = args


def start():
    parser = create_parser()
    args = parser.parse_args()
    if args.config:
        config_dict = load_yaml_from_file(args.config)
    else:
        config_dict = load_yaml_from_file(f"{ROOT_PATH}/config/config.yml")
    config = create_config(Config, config_dict)  # type: Config
    setup(config, args)
    logger.info(args)

    if hasattr(args, "command"):
        m = importlib.import_module(f'tv_info.command.{args.command}')
        m.start(config)
    else:
        parser.print_help()
        raise RuntimeError(f"unknown command")

    logger.debug(f"Finish: {args}")
