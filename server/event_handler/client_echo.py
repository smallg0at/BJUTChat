#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""调试client与server通信"""


from common.message import MessageType
from pprint import pprint
import server.memory
from common.util import md5
from server.util import database
import logging
logger = logging.getLogger(__name__)

def run(sc, parameters):
    logging.info(['client echo: %s', parameters])
    sc.send(MessageType.server_echo, parameters)
