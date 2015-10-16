#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author  :   'Victor'
# E-mail  :   linxianwusx@gmail.com
# Date    :   '2015/10/11'
# Version ：  0.3
#

import Queue
import ConfigParser
import os
import requests
import threading
import cchardet
import re
import sqlite3 as sq
import time
import jsonpickle

NUM = 0
mutex = threading.Lock()
requests.packages.urllib3.disable_warnings()  # Not show requests error messages

def monkey_patch():
    #requests库补丁
    #http://www.sdc1992.com/2015/04/08/Python-Requests抓取网页时编码错误的解决方案/
    prop = requests.models.Response.content
    def content(self):
        _content = prop.fget(self)
        if self.encoding == 'ISO-8859-1' or not self.encoding :
            encodings = requests.utils.get_encodings_from_content(_content)
            if encodings:
                self.encoding = encodings[0]
            else:
                # self.encoding = self.apparent_encoding
                self.encoding = cchardet.detect(_content)['encoding']
            #_content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace') 这个地方不能加这句话
            #返回的content是ascii码，根据返回的ascii码和response.encoding来处理字符串
            self._content = _content
        return _content
    requests.models.Response.content = property(content)

monkey_patch()

class Item(object):
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

    @staticmethod
    def getTime():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


class Downloader(object):

    def __init__(self, name, timeOut, urlList, downloadedNum, queue, mutLine, proxy):
        self.queue = queue
        self.name = name
        self.timeOut = timeOut
        self.downloadedNum = downloadedNum
        self.urlList = urlList
        self.threadList = []
        self.mutLine = mutLine
        self.proxy = proxy

    def getItem(self):
        """ use UrlList to distribute tasks and remove tasks url from UrlList """
        global NUM
        global mutex
        mutex.acquire()
        if self.urlList:
            url = self.urlList.pop(0)
            NUM += 1
            mutex.release()
            return [str(NUM + self.downloadedNum), url]
        else:
            mutex.release()
            return None

    def getHtml(self, url, timeOut):
        try:
            proxies = {}
            if self.proxy is not None:
                proxies = {
                    "http":   self.proxy,
                    "https":   self.proxy,
                }
            user_agent = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER'}
            response = requests.get(
                url, timeout=timeOut, headers=user_agent, proxies=proxies, verify=False)
            if response.status_code == requests.codes.ok:
                return response.content.decode(response.encoding,'ignore').encode("utf-8")
            else:
                response.raise_for_status()
                #raise Exception("HttpError", "Not response ok code !")
        except Exception as e:
            return e

    def download(self):
        while True:
            retry = 0
            temp = self.getItem()
            if not temp:
                break  # if there are none new item, stop download
            item = Item(temp[0], temp[1])
            html = self.getHtml(item.website, self.timeOut)
            # if download html some error, retry
            while not isinstance(html, str):
                print item.name, "\tRetry: " + str(html)  # 如果出错，html为出错信息
                retry += 1
                html = self.getHtml(item.website, self.timeOut)
                # if retry 3 times, if will finished download and set html =
                # "None"
                if retry >= 2 and (not isinstance(html, str)):
                    html = "None"
            item.setHtml(html)
            self.queue.put(jsonpickle.encode(item))
            global mutex
            mutex.acquire()
            if html != "None":
                print item.name, "\tDone"
            else:
                print item.name, "\tError"
            mutex.release()
        # print "Thread finished"

    def run(self):
        for i in xrange(self.mutLine):
            self.threadList.append(threading.Thread(target=self.download))
        for i in xrange(self.mutLine):
            self.threadList[i].start()

    def join(self):
        for i in xrange(self.mutLine):
            self.threadList[i].join()


class InsertDB(object):

    def __init__(self, queue, name):
        self.isWork = 1
        self.name = name
        self.queue = queue
        self.cx = sq.connect(self.name + ".db", check_same_thread=False)
        self.cx.text_factory = str
        self.cu = self.cx.cursor()

    def run(self):
        self.insertDB = threading.Thread(target=self.insertDb)
        self.insertDB.start()

    def getItemList(self):
        itemList = []
        num = 50  # Default once get 50 items.
        while self.queue.qsize() < num:  # wait for the queue enough 50 items.
            if self.isWork == 1:
                time.sleep(1)
            else:  # if downloader is finish, get queue size as new num value
                num = self.queue.qsize()

        for i in xrange(num):
            item = self.queue.get()
            itemList.append(self.item2List(item))
        return itemList

    @staticmethod
    def item2List(itemJson):
        item = jsonpickle.decode(itemJson)
        list1 = [item.time, item.website, item.html]
        return list1

    def insertDb(self):
        while True:
            itemList = self.getItemList()
            for i in itemList:
                # i：item.time, item.website, item.html
                # there should judge is newly added or failed to download
                self.cu.execute(
                    "SELECT count(id) FROM main WHERE website = ?", (i[1],))
                item = self.cu.fetchone()
                if item[0] == 0:  # new one
                    try:
                        self.cu.execute(
                            "INSERT INTO main(time, website, html) VALUES(?,?,?)", i)
                    except Exception as e:
                        print i
                else:  # failed and downloaded
                    self.cu.execute(
                        "UPDATE main SET html = ? WHERE website = ?", (i[2], i[1]))
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


class ListDownloader(object):

    def __init__(self, configPath):
        cf = ConfigParser.ConfigParser()
        cf.read(configPath)
        self.name = cf.get('LD', "Name")
        self.proxy = cf.get('LD', "Proxy")
        self.mutLine = cf.getint("LD", "MutLine")
        self.timeOut = cf.getint("LD", "timeOut")
        self.queue = Queue.Queue()
        self.downloadedNum = 0
        self.urlList = []
        print "READ CONFIG OK".center(30, "*")

    def createDB(self):  # create database
        cx = sq.connect(self.name + ".db")
        cu = cx.cursor()
        sql = "CREATE TABLE main(id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT,website BLOB, html BLOB);"
        cu.execute(sql)
        cu.close()
        cx.close()
        print "CREATE DATABASE OK".center(30, "*")

    def getDownloadUrlList(self):
        # 读取下载列表
        originUrl = []
        with open(self.name + "_url.txt") as f:
            for line in f.readlines():
                originUrl.append(line.strip("\n").decode("utf-8"))

        # 读取数据库下载列表
        cx = sq.connect(self.name + ".db")
        cu = cx.cursor()
        sql = "SELECT website FROM main;"
        cu.execute(sql)
        downloadedUrl = []
        for i in cu.fetchall():
            downloadedUrl.append(i[0])

        # 读取下载失败列表
        sql = "SELECT website FROM main WHERE html='None';"
        cu.execute(sql)
        errorUrl = []
        for i in cu.fetchall():
            errorUrl.append(i[0])

        cx.close()
        # 做差计算未下载列表
        url = [i for i in originUrl if i not in downloadedUrl]
        url.extend(errorUrl)
        print "LOAD DOWNLOAD LIST OK".center(30, "*")
        print "ALL\tNEED\tERROR"
        print str(len(originUrl)) + "\t" + str(len(url)) + "\t" + str(len(errorUrl))
        return [len(downloadedUrl) - len(errorUrl), url]

    def run(self):
        if not os.path.exists(self.name + ".db"):  # if there are no database file, than create one.
            self.createDB()
        else:
            print "FIND DATABASE OK".center(30, "*")

        self.downloadedNum, self.urlList = self.getDownloadUrlList()
        print "START DOWNLOAD".center(30, "*")
        downloader = Downloader(
            name = self.name,
            urlList = self.urlList,
            downloadedNum = self.downloadedNum,
            timeOut = self.timeOut,
            queue = self.queue,
            mutLine = self.mutLine,
            proxy = self.proxy
        )
        downloader.run()
        insertDB = InsertDB(self.queue, self.name)
        insertDB.run()

        downloader.join()
        insertDB.join()

if __name__ == "__main__":
    import sys
    ListDownloader(sys.argv[1]).run()
