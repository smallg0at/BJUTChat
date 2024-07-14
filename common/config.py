#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""获取配置文件信息"""

import json
from pprint import pprint
import sys, os


def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

with open(resourcePath('config.json')) as config_file:
    config = json.load(config_file)


def get_config():
    return config