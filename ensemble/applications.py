import os
import sys

import logging
import logging.config

import argparse
import json

from encore import resources

DEFAULT_CONFIG = {}

parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default=None)
parser.add_argument("-c", "--config", nargs='?', help="set config path")
parser.add_argument("-v", "--verbose", help="enable verbose output", action="store_true")
args, _ = parser.parse_known_args()

logging.config.dictConfig({
    'disable_existing_loggers': False,
    'formatters': {
        'console_formatter': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        },
        'file_formatter': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": logging.DEBUG if args.verbose else logging.WARNING,
            "formatter": "console_formatter",
            "stream": "ext://sys.stdout"
        },
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": logging.DEBUG,
            "formatter": "file_formatter",
            "filename": "default.log",
            "maxBytes": 1024*1024,
            "backupCount": 20,
            "encoding": "utf8"
        },
    },
    "root": {
        "level": logging.DEBUG,
        "handlers": ["console_handler", "file_handler"]
    },
    'version': 1,
})


def load_json(path):
    with open(path, "r") as f:
        value = json.load(f)
        return value

def save_json(path, value):
    with open(path, "w") as f: 
        json.dump(value, f)


def hostname():
    import socket
    return socket.gethostname()


def data_path(*args):
    return resources.application_path("data", *args)


def config_path():
    if args.config:
        return args.config
    
    filename = hostname() + ".cfg"
    path = resources.application_path("data/scripts", filename)
    if os.path.isfile(path):
        return path
    
    filename = "default.cfg"
    path = resources.application_path("data/scripts", filename)
    if os.path.isfile(path):
        return path


def get_config():
    from . import configurations
    
    def _get_config():
        try:
            path = config_path()
            return load_json(path)
        except:
            return DEFAULT_CONFIG
    
    config = _get_config()
    config = {} if config is None else config
    return configurations.Configuration(config)
