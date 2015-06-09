#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author  :   'Victor'
# E-mail  :   linxianwusx@gmail.com
# Date    :   '2015/6/6'
#
from Share import *
from Downloader import * 
from InsertDB import *
import Queue

class Spider():
    def __init__(self,mutLine):
        self.queue = Queue.Queue()    # [item1,item2]
        self.urlList = Queue.Queue()  # [[name1, url1],[name2, url2]]
        self.mutLine = mutLine

    def createDB(self):  # create database before start a spider
        cx = sq.connect("store.db")
        cu = cx.cursor()
        cu.execute("drop table if exists main;")
        cu.execute("create table main(id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT,name BLOB, website BLOB, html TEXT);")
        cu.close()
        cx.close()

    def getTitle(self):
        url =\
["http://www.pythontip.com//pythonPatterns/detail/abstract_factory",
"http://www.pythontip.com//pythonPatterns/detail/adapter",
"http://www.pythontip.com//pythonPatterns/detail/borg",
"http://www.pythontip.com//pythonPatterns/detail/bridge",
"http://www.pythontip.com//pythonPatterns/detail/builder",
"http://www.pythontip.com//pythonPatterns/detail/chain",
"http://www.pythontip.com//pythonPatterns/detail/command",
"http://www.pythontip.com//pythonPatterns/detail/composite",
"http://www.pythontip.com//pythonPatterns/detail/decorator",
"http://www.pythontip.com//pythonPatterns/detail/facade",
"http://www.pythontip.com//pythonPatterns/detail/factory_method",
"http://www.pythontip.com//pythonPatterns/detail/flyweight",
"http://www.pythontip.com//pythonPatterns/detail/graph_search",
"http://www.pythontip.com//pythonPatterns/detail/iterator",
"http://www.pythontip.com//pythonPatterns/detail/mediator",
"http://www.pythontip.com//pythonPatterns/detail/memento",
"http://www.pythontip.com//pythonPatterns/detail/null",
"http://www.pythontip.com//pythonPatterns/detail/observer",
"http://www.pythontip.com//pythonPatterns/detail/pool",
"http://www.pythontip.com//pythonPatterns/detail/prototype",
"http://www.pythontip.com//pythonPatterns/detail/proxy",
"http://www.pythontip.com//pythonPatterns/detail/state",
"http://www.pythontip.com//pythonPatterns/detail/strategy",
"http://www.pythontip.com//pythonPatterns/detail/template",
"http://www.pythontip.com//pythonPatterns/detail/visitor"]
        import re
        p = re.compile(r'detail\/(\S+)')
        for i in url:
            titles = p.findall(i)
            self.urlList.put([titles[0],i])

    def run(self):
        self.createDB()
        self.getTitle()

        downloader = Downloader(self.urlList,self.queue,self.mutLine)
        downloader.run()
        insertDB = InsertDB(self.queue)
        insertDB.run()

        downloader.join()
        insertDB.join()

if __name__ == "__main__":
    Spider(30).run()
