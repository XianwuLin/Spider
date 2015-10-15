#!/usr/bin/env python
# -*- coding:utf-8 -*-
##过滤数据库中的html，提取全文信息
import sqlite3 as sq
import re


##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('<!\[CDATA(.|\n)*?\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script(.|\n)*?>(.|\n)*?<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style(.|\n)*?>(.|\n)*?<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('<(.|\n)*?>')#广义HTML标签
    re_comment=re.compile('<!--(.|\n)*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n[\s| ]*\n')
    s=blank_line.sub('',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)


def clearBrokenHtml(name):
    cx = sq.connect(name + ".db")
    cu = cx.cursor()
    cx.text_factory = str

    sql = 'delete from main where html = "None";' #清空未成功下载的html
    cu.execute(sql)
    cx.commit()

    sql = "select id, html from main"
    cu.execute(sql)
    counter = 0 #清理计数器
    for j in cu.fetchall():
        html = j[1].strip()
        if html[-7:] != "</html>":  #清空结构不完整的
            sql = "delete from main where id = ?"
            cu.execute(sql,(str(j[0]),))
            cx.commit()
            counter += 1
    print "clear ", str(counter)
    print u"Clear Broken Html OK!"
    print

def addField(name):
    cx = sq.connect(name + ".db")
    cu = cx.cursor()
    try:
        cu.execute("alter table main add column content BLOB;")
        cx.commit()
    except:
        pass
    finally:
        cx.close()

def main(name):
    cx = sq.connect(name + ".db")
    cu = cx.cursor()
    cx.text_factory = str
    sql = "select id, html from main"
    cu.execute(sql)
    htmlList =  cu.fetchall()
    counter = 0 #计数器
    for i in htmlList:
        html = i[1].strip()
        content = filter_tags(html)
        sql = "update main set content = ? where id = ?"
        cu.execute(sql,(content,i[0]))
        counter += 1
        if counter == 50:
            cx.commit()
            print '.',
            counter = 0
    cx.commit()
    cx.close()
    print

if __name__ == '__main__':
    import sys
    import ConfigParser

    cf = ConfigParser.ConfigParser()
    cf.read(sys.argv[1])
    name = cf.get('LD',"Name")

    clearBrokenHtml(name)
    addField(name)
    main(name)
