#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author  :   'Victor'
# E-mail  :   linxianwusx@gmail.com
# Date    :   '2015/6/6'
#

from Spider import *
from Share import *
from Item import *
import urllib2
import jsonpickle
import threading


class Downloader():
    def __init__(self,urlList,queue,mutLine):
        self.queue = queue
        self.urlQueue = urlList
        self.threadList = []
        self.mutLine = mutLine

    def getItem(self):  # OVERRIDE this function to change crawl any urls
        if self.urlQueue.empty():
            global isWork
            isWork = 0
            return None
        else:
            return self.urlQueue.get()

    def getHtml(self, url, timeOut):
        try:
            opener = urllib2.Request(url)
            r = urllib2.urlopen(opener, timeout=timeOut)
            t = r.read()
            return t
        except:
            return None

    def download(self):
        while True:
            temp = self.getItem()
            if not temp:
                break # if there are none new item, stop download
            item = Item(temp[0],temp[1])
            html = self.getHtml(item.website, 10)
            while (not html):   # if download html some error, retry
                print item.name, "\tRetry"
                html = self.getHtml(item.website, 10)
            item.setHtml(html)
            #print jsonpickle.encode(item)
            self.queue.put(jsonpickle.encode(item))
            global mutex
            mutex.acquire()
            print item.name, "\tDone"
            mutex.release()
        #print "Thread finished"

    def run(self):
        for i in xrange(self.mutLine):
            self.threadList.append(threading.Thread(target=self.download))
        for i in xrange(self.mutLine):
            self.threadList[i].start()

    def join(self):
        for i in xrange(self.mutLine):
            self.threadList[i].join()
