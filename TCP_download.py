#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Victor Lin
#   E-mail  :   linxianwusx@gmail.com
#   Date    :   15/02/19 20:45:28
#

import cookielib, urllib2
import time
import sys
import socket
import Cookie
import urllib
import os

socket.setdefaulttimeout(60)


class HackWeb():
    def __init__(self):
        self.user_agent = '''Mozilla/5.0 (Linux; U; Android 4.2.1; zh-cn; HUAWEI G700-U00 Build/HuaweiG700-U00) AppleWebKit/533.1 (KHTML, like Gecko)Version/4.0 MQQBrowser/5.4 TBS/025410 Mobile Safari/533.1 MicroMessenger/6.1.0.66_r1062275.542 NetType/WIFI'''
        self.cookies_site = "http://lancaster.ifm-paris.cn/Wechat/oauth2?callback=http://lancasterld.samesamechina.com/"
        self.cj = None

    def set_cookies(self):
        req = urllib2.Request(self.cookies_site)
        req.add_header('User-Agent', self.user_agent)
        self.cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        opener.open(req)
        self.lf = open("cc.txt",'a')
        self.lf.write(str(self.cj))
        self.lf.write('\n')
        self.lf.close()
        return str(self.cj)


    def post(self,url,data):
        req = urllib2.Request(url,data)
        req.add_header('User-Agent', self.user_agent)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        f = opener.open(req)
        htm = f.read()
        f.close()
        self.lf = open("cc.txt",'a')
        self.lf.write(htm)
        self.lf.write("\n")
        self.lf.close()
        return htm

    def get(self,url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.user_agent)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        f = opener.open(req)
        htm = f.read()
        f.close()
        self.lf = open("cc.txt",'a')
        self.lf.write(htm)
        self.lf.write("\n")
        self.lf.close()
        return htm

def run():
    import json
    hackweb = HackWeb()
    hackweb.set_cookies()
    token = hackweb.get("http://lancasterld.samesamechina.com/access_token/access_token.php")
    num = (json.loads(token))["time"]
    print num


    #c = cookielib.Cookie(version=0, name='__utma', value='154667882.547793256.1425536347.1425554928.1425564399.4', port=None, port_specified=False, domain='clinique.iprotime.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    #cj.set_cookie(c)

if __name__ == "__main__":
    run()
