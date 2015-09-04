# -*- coding: UTF-8 -*-
import sqlite3 as sq
import re
import time
from multiprocessing import Process, Queue, Lock, Value
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

def getList(website, html):
    html = unicode(html)
    title_url = re.compile('<span class="article-title">(.+?)</span>',re.S).findall(html)
    titles = []
    for i in title_url:
        titles += re.compile(">(.+)<").findall(i)
    content = re.compile('<div class="summary-text">(.+?)</div>',re.S).findall(html)
    joke_dict = dict(zip(titles, content))
    return joke_dict

def get_max_id():
    cx = sq.connect("store.db")
    cx.text_factory = str
    cu = cx.cursor()
    cu.execute("select max(id) from main;")
    max_id = cu.fetchone()[0]
    cx.close()
    return max_id
    
class Pipeline():
    def __init__(self):
        cx = sq.connect("store.db")
        cu = cx.cursor()
        cu.execute("drop table if exists jokes;")
        cu.execute("create table jokes(id INTEGER PRIMARY KEY AUTOINCREMENT,website BLOB,title TEXT,joke TEXT);")
        cx.close()
        self.max_id = get_max_id()

    def get_id(self,lock,queue):
        lock.acquire() #还是需要有锁的
        id = queue.get()
        queue.put(id+1)
        lock.release()
        return id
    
    def main(self, lock, queue, jockqueue):
        cx = sq.connect("store.db")
        cx.text_factory = str
        cu = cx.cursor()
        id = self.get_id(lock,queue)
        while id <= self.max_id:
            sql = "select website,html from main where id=" + str(id)
            cu.execute(sql)
            [website,html] = cu.fetchone()
            jockList = getList(website, html)
            for k in jockList.keys():
                 jockqueue.put([website,k,jockList[k]])
            id = self.get_id(lock,queue)
            lock.acquire()
            print id
            lock.release()
            
    def insertDB(self,jockqueue, message):
        cx = sq.connect("store.db")
        cx.text_factory = str
        cu = cx.cursor()
        while True:
            for i in xrange(jockqueue.qsize()):
                cu.execute("insert into jokes(website, title, joke) values(?,?,?)", jockqueue.get())
            cx.commit()
            while jockqueue.qsize() < 1:
                time.sleep(0.1)
                if message.value == 1:
                    return
            
    def run(self,mutilLine):
        queue = Queue()
        jockLists = Queue()
        message_queue = Queue()
        lock = Lock()
        queue.put(1)
        message = Value('i', 0)
        insert_process = Process(target=self.insertDB,args=(jockLists, message))
        insert_process.start()
        p = [Process()]*mutilLine
        for i in range(mutilLine):
            p[i] = Process(target=self.main, args=(lock, queue, jockLists))
            p[i].start()
        for i in range(mutilLine):
            p[i].join()
        message.value = 1 #分析完毕
        insert_process.join()
        print "finished!"

if __name__ == "__main__":
    pipeline = Pipeline().run(20)