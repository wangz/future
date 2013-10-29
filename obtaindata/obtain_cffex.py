#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
# pip install BeautifulSoup MySQL-python
# from 20100416
import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment
from datetime import * 
import time,logging,MySQLdb
import re
import xml.dom.minidom
import dbconf

reload(sys) 
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='futures.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG)
# console = logging.StreamHandler();
# console.setLevel(logging.INFO);
# # set a format which is simpler for console use
# formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s');
# # tell the handler to use this format
# console.setFormatter(formatter);
# logging.getLogger('').addHandler(console);

query1 = "insert into trading(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query2 = "insert into longpos(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query3 = "insert into shortpos(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"

url_date = "20130918"

logging.info("argv count:%s" %  len(sys.argv))
if len(sys.argv)>1:
    if sys.argv[1]!=None:
        url_date = sys.argv[1]
else:
    logging.info("未输入日期，则默认处理当前数据!")
    now = date.today()
    url_date = now.strftime('%Y%m%d')
logging.info("处理日期 url_date: %s",url_date)
'''obtain futures data'''
url_one = "http://www.cffex.com.cn/fzjy/ccpm/%s/%s/index.xml" % (url_date[0:6],url_date[6:8])

try:
    f = None
    req = urllib2.Request(url=url_one)
    req.add_header('Context-Type', 'application/xml')
    f = urllib2.urlopen(req)   
    rawdata = f.read()

    if f.geturl().find('error_404') > 0 :
        logging.error("此日期无信息！URL：%s" % url_date)
        exit(0)
except Exception,e:
    logging.error("下载此页信息失败！URL：%s" % url_one)
    logging.error(e)
    exit(1)
finally:
    if f!=None:
        f.close()

# f2=open('data_cffex_20130918.xml','w')
# f2.write(rawdata)
# f2.close()

# f3= open('data_cffex_20130918.xml','r')
# rawdata = f3.read()
# f3.close()

#delete already get data
conn = None
cursor = None
try:
    conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
    cursor = conn.cursor()
    delete_sql = "delete from longpos where origin='%s' and pub_date=%s;\
    delete from shortpos where origin='%s' and pub_date=%s;\
    delete from trading where origin='%s' and pub_date=%s;" 

    check_sql = "select count(*) from longpos where origin='%s' and pub_date=%s;"
    
    cursor.execute(check_sql % ('中金',url_date))
    logging.info("already get data count need delete: %s" %  cursor.fetchall()[0][0])

    cursor.execute(delete_sql % ('中金',url_date,'中金',url_date,'中金',url_date))
    logging.info(delete_sql %  ('中金',url_date,'中金',url_date,'中金',url_date))
except Exception,e:
    logging.error(" MySQL server exception!!!")
    logging.error(e)
    sys.exit(1)
finally:
    if cursor!= None:
        cursor.close()
    if conn!= None:
        conn.commit()
        conn.close()

ishasdata = False
logging.info("处理URL为：%s" % url_one)

# http://blog.sina.com.cn/s/blog_6d7e5bc301011mvv.html
rawdata = rawdata.replace('encoding="GBK"','encoding="utf-8"')
rawdata = unicode(rawdata,encoding='gbk').encode('utf-8')

dom = xml.dom.minidom.parseString(rawdata)


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


data_c = 0
for e in dom.getElementsByTagName("data"):
    data_c+=1
logging.info( "find data count = %s" % data_c)

if data_c > 3:
    ishasdata = True
    logging.info("obtain data success,start process")
else:
    logging.warning("此页未找到足够数据！obtain data failed date: %s" % url_one)
    exit(0)

for index,e in enumerate(dom.getElementsByTagName("data")):

    shortname = e.getElementsByTagName('shortname')
    instrument = e.getElementsByTagName('instrumentId')
    dataType = e.getElementsByTagName('dataTypeId') # 0chengjiao 1买danliang 2maidanliang
    value = e.getElementsByTagName('volume')

    instrument = getText(instrument[0].childNodes).strip()
    shortname = getText(shortname[0].childNodes).strip()
    dataType = getText(dataType[0].childNodes).strip()
    value = getText(value[0].childNodes).strip()
    
    try:
        conn = None
        cursor = None
        conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
        cursor = conn.cursor()
        if dataType == '0':
            logging.info(query1 % ('中金',instrument,shortname,'成交量',value,url_date))
            cursor.execute(query1,('中金',instrument,shortname,'成交量',value,url_date))
        if dataType == '1':
            logging.info(query2 % ('中金',instrument,shortname,'持买单量',value,url_date))
            cursor.execute(query2,('中金',instrument,shortname,'持买单量',value,url_date))
        if dataType == '2':
            logging.info(query3 % ('中金',instrument,shortname,'持卖单量',value,url_date))
            cursor.execute(query3,('中金',instrument,shortname,'持卖单量',value,url_date))
    except Exception,e:
        logging.error(" MySQL server exception!!!")
        logging.error(e)
        sys.exit(1)
    finally:
        if cursor!= None:
            cursor.close()
        if conn!= None:
            conn.commit()
            conn.close()
    
time.sleep(1)  

from smtpmail import send_mail
send_mail(["51649548@qq.com"],"中金持仓提取情况","%s数据 日期%s 提取完成" % ('中金',url_date))
send_mail(["aaronfu@triumphantbank.com"],"中金持仓提取情况","%s数据 日期%s 提取完成" % ('中金',url_date))
send_mail(["johlu@triumphantbank.com"],"中金持仓提取情况","%s数据 日期%s 提取完成" % ('中金',url_date))
send_mail(["dangwannian@triumphantbank"],"中金持仓提取情况","%s数据 日期%s 提取完成" % ('中金',url_date))




          
        


