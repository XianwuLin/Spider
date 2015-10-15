#!/usr/bin/env python
# -*- coding:utf-8 -*-
###
###对数据库进行分词
import sqlite3 as sq
import jieba
import re

def delblankline(text): #删除空行
    filtedLines = []
    lines = text.split("\n")
    for li in lines:
        if li.split():
            filtedLines.append((re.sub(r'\s+', ' ', li)))
    return "\n".join(filtedLines)

def delblankline1(text): #删除所有空格
    return "".join(text.split())


def addField(name):
    cx = sq.connect(name + ".db")
    cu = cx.cursor()
    try:
        cu.execute("alter table main add column part BLOB;")
        cx.commit()
    except:
        pass
    finally:
        cx.close()

def getPartList(name):
        cx = sq.connect(name + ".db")
        cu = cx.cursor()
        cx.text_factory = str
        cu.execute("select id, content from main")
        number = 0 #插入计数器
        for i in cu.fetchall():
            partList = []
            id = i[0]
            content = i[1]
            text = delblankline1(content)
            seg_list = jieba.cut(text, cut_all=False)
            for i in seg_list:
                if len(i):
                    partList.append(i)
            cu.execute("UPDATE main set part=? where id =?",(" ".join(partList),id))
            number += 1
            if number == 50:
                cx.commit()
                number = 0
                print '.',
        cx.commit()
        cx.close()

if __name__ == "__main__":
    import sys
    import ConfigParser

    cf = ConfigParser.ConfigParser()
    cf.read(sys.argv[1])
    name = cf.get('LD',"Name")

    addField(name)
    getPartList(name)