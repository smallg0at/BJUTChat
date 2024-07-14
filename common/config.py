#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""获取配置文件信息"""

import json
from pprint import pprint
from os import path
path_to_dat = path.abspath(path.join(path.dirname(__file__), '../config.json'))

with open(path_to_dat) as config_file:
    config = json.load(config_file)


def get_config():
    return config