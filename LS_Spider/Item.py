#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author  :   'Victor'
# E-mail  :   linxianwusx@gmail.com
# Date    :   '2015/6/6'
#

import time

class Item():
    html = ""
    website = ""
    name = ""
    time = ""

    def __init__(self, name, website):
        self.website = website
        self.name = name
        self.time = self.getTime()

    def setHtml(self, html):
        self.html = html

    def getTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))