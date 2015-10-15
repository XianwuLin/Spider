# -*- coding: utf-8 -*-
"""
多文件批量下载器，采用队列多线程下载
"""
import Queue
import urllib
import threading
import socket
import time

_use_line = 10
_t = 0
_time = 0

class _start_download(threading.Thread):
    socket.setdefaulttimeout(60)

    def __init__(self, file_url, file_name):
        threading.Thread.__init__(self)
        self.url = file_url
        self.name = file_name

    def run(self):
        global  _use_line
        global _t
        _use_line -= 1
        global _time
        try:
            urllib.urlretrieve(self.url, self.name)
            print self.name, "is downloaded.", "\tSpeed:", round(_t/(time.time() - _time),2), "/s\tTotal: ", _t
        except Exception as e:
            print e
        _use_line += 1
        _t += 1

def download(download_url, file_url, folder="E:/download/"):
    q = Queue.Queue(0)
    global _time
    _time = time.time()
    global _use_line
    _use_line = 10
    file_list = file_url
    download_list = download_url

    for i in range(len(download_list)):
        q.put((download_list[i], folder + file_list[i]))

    print "*** START DOWNLOAD ***"
    while (not q.empty()):
        if (_use_line > 0):
            for i in range(_use_line):
                dl = q.get()
                c = _start_download(dl[0], dl[1])
                c.start()
        else:
            time.sleep(0.1)
    print "*** END DOWNLOAD ***"

if __name__ == '__main__':
    import sqlite3
    import re

    con = sqlite3.connect('item.db')
    cu = con.cursor()
    cu.execute('Select url from image')
    image = cu.fetchall()

    image_list = []
    image_name = []
    for i in image:
            image_t = i[0].encode("utf-8")
            name = re.findall('[0-9a-zA-Z-]+\.jpg|[0-9a-zA-Z-]+\.JPG|[0-9a-zA-Z-]+\.png|[0-9a-zA-Z-]+\.PNG',image_t)
            image_list.append(image_t)
            image_name.append(name[0])

    cu.close()
    download(image_list, image_name, 'e:/temp/')
