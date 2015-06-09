#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author  :   'Victor'
# E-mail  :   linxianwusx@gmail.com
# Date    :   '2015/6/6'
#
from Share import *
import sqlite3 as sq
import time
import jsonpickle

class InsertDB():
    def __init__(self,queue):
        self.isWork = 1
        self.queue = queue
        self.cx = sq.connect("store.db",check_same_thread = False)
        self.cu = self.cx.cursor()

    def run(self):
        self.insertDB = threading.Thread(target=self.insertDb)
        self.insertDB.start()

    def getItemList(self,):
        itemList = []
        num = 50 # Default once get 50 items.
        while self.queue.qsize() < num : # wait for the queue enough 50 items.
            if self.isWork == 1:
                time.sleep(1)
            else: # if downloader is finish, get queue size as new num value
                num = self.queue.qsize()

        for i in xrange(num):
            itemList.append(self.item2List(self.queue.get()))
        return itemList

    def item2List(self,itemJson):
        item = jsonpickle.decode(itemJson)
        list1 = [item.time,item.name,item.website,item.html]
        return list1

    def insertDb(self):
        while True:
            itemList = self.getItemList()
            for i in itemList:
                self.cu.execute("insert into main(time, name, website, html) values(?,?,?,?)", i)
            self.cx.commit()
            if self.isWork == 0:
                self.cu.close()
                self.cx.close()
                break
            if len(itemList) == 0:
                break

    def join(self):
        self.isWork = 0
        self.insertDB.join()
