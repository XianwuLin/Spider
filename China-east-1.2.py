#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Victor Lin
#   E-mail  :   linxianwusx@gmail.com
#   Date    :   15/03/30 16:50:18
#
from bs4 import BeautifulSoup
import urllib2
from math import ceil
import threading
import re
import time
import os
import sys

ganggu_session = None
p = []
listL = []
errorList = []
reload(sys)
sys.setdefaultencoding("utf-8")
mutex = threading.Lock()

def funcWithTimeout(timeout): #线程控制整体程序超时
    t1 = threading.Thread(target = section)
    t1.setDaemon(True)
    t1.start()
    t1.join(timeout)

def download(site): #列表下载
    aString, code = site
    try:
        opener = urllib2.Request("http://hqdigi2.eastmoney.com/EM_Quote2010NumericApplication/index.aspx?type=s&sortType=C&sortRule=-1&pageSize=2000&jsName=quote_123&style="+str(code)+"&token=44c9d251add88e27b65ed86506f6e5da&_g=0.6590099500026554")
        r = urllib2.urlopen(opener,timeout=10)
        t = r.read()

        pattern = re.compile(r'"\S+\s\S+[^,]"')
        matchAll = pattern.findall(t)
        for i in matchAll:
            temp = i[1:-1].split(',')
            n = temp[0][-1]
            code = temp[1]
            name = unicode(temp[2])
            s = "sz" if int(n) == 2 else "sh"
            global mutex
            mutex.acquire()
            listL.append(aString + "," + s + code + "," + name)
            mutex.release()
        return 0
    except:
        print aString + u"\tError. Try again!"
        return 1

def funcWithTimeout(timeout): #线程控制整体程序超时
    t1 = threading.Thread(target = section)
    t1.setDaemon(True)
    t1.start()
    t1.join(timeout)

def ganggu():
    print u"开始下载港股"
    status = ganggu_download() #下载港股
    while(status != 0):
        status = ganggu_download()
        time.sleep(0.2)
    print u"港股下载完成"

def ganggu_download(): #港股下载
    try:
        opener = urllib2.Request("http://183.136.160.59/EM_Quote2010NumericApplication/index.aspx?type=s&sortType=C&sortRule=-1&pageSize=5000&page=1&jsName=quote_123&style=50&_g=0.7055022045969963")
        r = urllib2.urlopen(opener,timeout=20)
        t = r.read()
        listL1 = []
        pattern = re.compile(r'"\S+\s\S+[^,]"')
        matchAll = pattern.findall(t)
        for i in matchAll:
            temp = i[1:-1].split(',')
            n = temp[0][-1]
            code = temp[1]
            name = unicode(temp[2])
            s = "sz" if int(n) == 2 else "sh"
            listL1.append(name + "\t" + code + "\t" + "2")

        listL1.sort() #排序写入文件
        f = open('code','w')
        for i in listL1:
            f.write(i+"\n")
        f.close()
        return 0
    except:
        print u"港股 Error. Try again!"
        return 1

def downloadMuPage(siteList): #调用下载函数，防止发生HTTP错误
    for site in siteList:
        status = download(site)
        while(status != 0):
            status = download(site)
            time.sleep(0.2)
        global mutex
        mutex.acquire()
        print site[0] + "\tDone"
        mutex.release()

def mutDown(websiteList): #多线程分发
    mutLine = 10 #线程数
    first = int(ceil(len(websiteList) / float(mutLine)))
    global p
    p = []
    for i in xrange(mutLine):
        temp = websiteList[ first*i : first*(i+1) ]
        p.append(threading.Thread(target=downloadMuPage,args=(temp,)))
    for i in xrange(mutLine):
        p[i].start()
    for i in xrange(mutLine):
        p[i].join()

def section(): #爬虫主程序
    #删除旧文件
    if os.path.exists("section.txt"):
        os.remove("section.txt")
    if os.path.exists("list.txt"):
        os.remove("list.txt")

    opener = urllib2.Request("http://quote.eastmoney.com/center/list.html")
    r = urllib2.urlopen(opener,timeout=20)
    soup = BeautifulSoup(r.read())
    div = [None,None,None]
    div[0] = soup.find_all('div', "hover-pop col-7") #找出概念板块div
    div[1] = soup.find_all('div', "hover-pop col-3") #找出地域板块div
    div[2] = soup.find_all('div', "hover-pop col-4") #找出行业板块div
    for j in xrange(len(div)):
        soup = BeautifulSoup(str(div[j]))
        li1 = soup.find_all("a")  #找出div中的链接
        f = open('section.txt','a+')
        nameList = []
        downloadList = []
        for i in xrange(len(li1)):
            name = unicode(str(li1[i].string))
            aString = chr(65+j) + str(i+1).zfill(3)
            nameList.append(name)
            f.write(aString + "," + name + "\n")  #写入板块名称
            downloadList.append([ aString , str(li1[i].attrs['href'])[10:18] ]) #下载列表
        f.close()
        print chr(65+j),u"列表下载完成"
        mutDown(downloadList)
    print u"爬取结束，正在排序    ",
    storageFile() #储存板块文件

    global ganggu_session
    ganggu_session = threading.Thread(target = ganggu)
    ganggu_session.start()
    ganggu_session.join()

def storageFile():
    global listL
    listL.sort()
    print u"排序成功，正在写入文件    ",
    f = open("list.txt","a")
    for i in listL:
        f.write(i + "\n")
    f.close()
    print u"写入文件成功"

def main():#程序入口
    funcWithTimeout(300) #设置超时时间，单位 秒
    
    global p #板块下载
    a = 0
    for i in p:
        if i.is_alive():
            a = 1

    global ganggu_session #港股下载
    try:
        if ganggu_session.is_alive():
            a = 1
    except:
        pass

    return a

if __name__ == "__main__":
    print main()
