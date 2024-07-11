#!/usr/bin/env python
# -*- coding:utf-8 -*-

import file_server.app

file_server.app.app.run(debug=True, port=5000)