#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Victor Lin
#   E-mail  :   linxianwusx@gmail.com
#   Date    :   15/06/09 16:33:02
#
from bs4 import BeautifulSoup
import sqlite3 as sq
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

cx = sq.connect("store.db")
cu = cx.cursor()
f = open('123.md','w')
for i in xrange(1,26):
    cu.execute("select name, html from main where id = ?",(i,))
    name, html = cu.fetchone()
    soup= BeautifulSoup(html)
    div = soup.find_all(id='editor-code')
    code = div[0].string
    f.write(unicode(name))
    f.write("\n---\n```\n")
    f.write(code)
    f.write("\n```\n\n--------------\n")
f.close()
