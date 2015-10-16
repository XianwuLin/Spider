#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from BeautifulSoup import BeautifulSoup as bs
import urlparse
from urllib2 import HTTPError
import ConfigParser
import os
import cchardet
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')


def monkey_patch():
    # requests库补丁
    # http://www.sdc1992.com/2015/04/08/Python-Requests抓取网页时编码错误的解决方案/
    prop = requests.models.Response.content

    def content(self):
        _content = prop.fget(self)
        if self.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(_content)
            if encodings:
                self.encoding = encodings[0]
            else:
                # self.encoding = self.apparent_encoding
                self.encoding = cchardet.detect(_content)['encoding']
                _content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace')
            self._content = _content
        return _content

    requests.models.Response.content = property(content)


monkey_patch()


def getHtml(url, timeOut):
    try:
        proxies = {
            # "http": "127.0.0.1:1080",
        }
        user_agent = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER'}
        response = requests.get(
            url, timeout=timeOut, headers=user_agent, proxies=proxies, verify=False)
        if response.status_code == requests.codes.ok:
            return response.content
        else:
            response.raise_for_status()
            #raise Exception("HttpE#rror", "return code: " + str(response.status_code))
    except Exception as e:
        return e


def getDeepList(url, timeout=10, retryTimes=3):
    """根据urlList获取url对应的Html内的全部的链接，返回set(链接)"""
    deepUrlList = set()
    html = None
    parse = urlparse.urlparse(url)
    html = getHtml(url, timeout)
    retry = 0
    while not isinstance(html, str):  # if download html some error, retry
        if retry >= retryTimes:
            print url, str(html)
            break
        print url, "\tRetry: " + str(html)
        retry += 1
        html = getHtml(url, timeout)
    print url
    if isinstance(html, str):
        soup = bs(html)
        for item in soup.fetch('a'):
            if item.has_key('href'):
                urlNext = item['href']
                if len(urlNext) <= 1:  # 忽略引向本页的链接和空链接
                    continue
                if len(urlNext) < 4 or urlNext[:4] != "http":  # 判断网址是不是完全的，是不是包含了根目录
                    if urlNext[0] == "/":
                        urlNext = u"http://" + parse.netloc + urlNext
                    else:
                        urlNext = u"http://" + parse.netloc + u"/" + urlNext
                deepUrlList.add(urlNext)
    return deepUrlList

def main(name, startUrl, level, timeOut):
    """深度挖掘网址"""
    downloaded = set()
    urlList = set()
    urlList.add(startUrl)
    for i in range(level):
        for j in urlList:
            if j:
                urlListTemp = getDeepList(j, timeOut)
                downloaded.add(j)
                with open(name + "_url.txt", 'a') as f:
                    f.write("\n".join(urlListTemp).strip())
                urlList = urlList | urlListTemp  # - downloaded

                with open(name + "_url.txt", "r") as f:  # 文件内容去重
                    urlList = set()
                    for i in f.readlines():
                        url = i.strip()
                        if len(re.compile(r'http://').split(url)) > 2: #对于列表中中出现了http://123.123/http://123.123/这种情况进行处理
                            for j in re.compile(r'http://').split(url):
                                if len(j) > 1: #分出来第一个为空
                                    urlList.add(j)
                        else:
                            urlList.add(url)
                with open(name + "_url.txt", "w") as f:
                        f.write("\n".join(urlList).strip())


def main1(name, startUrl, width, timeOut):
    """水平挖掘网址"""

    for i in xrange(1, width + 1):
        url = startUrl % i
        urlList = getDeepList(url, timeOut)
        with open(name + "_url.txt", 'a') as f:
            f.write("\n".join(urlList))

        with open(name + "_url.txt", "r+") as f:  # 文件内容去重
            urlList = set()
            for i in f.readlines():
                urlList.add(i.strip())
                f.seek(0, 0);
                f.truncate()
                f.write("\n".join(urlList).strip())


if __name__ == "__main__":
    import sys

    cf = ConfigParser.ConfigParser()
    cf.read(sys.argv[1])
    name = cf.get('LD', "Name")
    mode = cf.getint('LF', "Mode")
    startUrl = cf.get('LF', 'StartUrl')
    level = cf.getint('LF', 'Level')
    timeOut = cf.getint('LD',"timeOut")

    if os.path.exists(name + '_url.txt'):  # 如果之前存在下载列表，则删除之
        os.remove(name + '_url.txt')
    if startUrl:  # 如果startUrl存在
        if mode == 1:  # 深度寻找
            main(name, startUrl, level, timeOut)
        elif mode == 2:  # 宽度寻找
            main1(name, startUrl, level, timeOut)
    else:  # 如果startUrl不存在，则寻找name_startUrl.txt文件
        with open(name + "_startUrl.txt", 'r') as f:
            startUrl = f.readline().strip()
            while startUrl:
                if mode == 1:  # 深度寻找
                    main(name, startUrl, level, timeOut)
                elif mode == 2:  # 宽度寻找
                    main1(name, startUrl, level, timeOut)
                startUrl = f.readline().strip()
