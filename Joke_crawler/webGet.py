#!/usr/bin/env python
# encoding: utf-8
# AUTHOR : VICTOR LIN
# EMAIL : linxianwusx@163.com
# Time : 2015/9/4 16:38
import sqlite3 as sq
import tornado.ioloop
import tornado.web
import json

def getAJoke():
    cx = sq.connect("store.db")
    cx.text_factory = str
    cu = cx.cursor()
    cu.execute("select title, joke from jokes order by RANDOM() limit 1")
    joke = cu.fetchone();
    return joke

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class GetNewJoke(tornado.web.RequestHandler):
     def get(self):
        joke = getAJoke()
        data = {"title":joke[0],"joke":joke[1]}
        print joke[0],joke[1]
        self.write(json.dumps(data))


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/getnewjoke",GetNewJoke),
])

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()