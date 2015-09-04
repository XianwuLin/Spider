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
        self.queue = Queue.Queue() 
        self.queue1 = Queue.Queue() #
        self.urlList = Queue.Queue()  # [[name1, url1],[name2, url2]]
        self.mutLine = mutLine

    def createDB(self):  # create database before start a spider
        cx = sq.connect("store.db")
        cu = cx.cursor()
        cu.execute("drop table if exists main;")
        cu.execute("create table main(id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT,name BLOB, website BLOB, html TEXT);")
        cu.close()
        cx.close()

    def run(self):
        self.createDB()

        downloader = Downloader(self.urlList,self.queue,self.mutLine)
        downloader.run()
        insertDB = InsertDB(self.queue, self.queue1)
        insertDB.run()

        downloader.join()
        insertDB.join()

if __name__ == "__main__":
    Spider(10).run()
