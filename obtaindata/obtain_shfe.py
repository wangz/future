#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
# pip install BeautifulSoup MySQL-python
import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment
from datetime import * 
import time,logging,MySQLdb
import re
import dbconf

reload(sys) 
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='future_shfe.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG)
 
query1 = "insert into data_trading(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query2 = "insert into data_buy(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query3 = "insert into data_selling(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"

url_date = "20130711"

if len(sys.argv)>1:
    if sys.argv[1]!=None:
        url_date = sys.argv[1]
else:
    now = date.today()
    url_date = now.strftime('%Y%m%d')
logging.info("处理日期 url_date: %s",url_date)
'''obtain futures data'''
url_one = "http://www.shfe.com.cn/dailydata/kx/pm%s.html" % url_date

try:
    f = None
    f = urllib2.urlopen(url_one)
    rawdata = f.read()
except Exception,e:
    logging.error("下载此页信息失败！URL：%s" % url_one)
    logging.error(e)
    exit(1)
finally:
    if f!=None:
        f.close()

##f2=open('data_20110311.htm','w')
##f2.write(rawdata)
##f2.close()

##f3= open('data_20110311.htm','r')
##rawdata = f3.read()
##f3.close()
ishasdata = False
logging.info("处理URL为：%s" % url_one)
table_c = 0
##re.sub(r'\s+', ' ', rawdata)
##print rawdata
##rawdata = BeautifulSoup(rawdata).prettify()
soup = BeautifulSoup(rawdata)
#value has comment,then cannot parse!!!so extract it
comments = soup.findAll(text=lambda text:isinstance(text, Comment))
print "len: %d " % len(comments)
[comment.extract() for comment in comments]

##f2=open('data_20110311_b.htm','w')
##f2.write(soup)
##f2.close()

for m in soup.findAll('table'):
    table_c+=1
logging.info( "find table count = %s" % table_c)

if table_c > 5:
    ishasdata = True
    logging.info("obtain data success,start process")
else:
    logging.warning("此页未找到足够数据！obtain data failed date: %s" % url_one)

if ishasdata:
    table_c = 0
    hydm = None #heyuedaima
    for m in soup.findAll('table'):   
        table_c+=1
        logging.info("processing table: %d" % table_c)
        if(m.get('id') == None):
            for mtd in m.findAll('td'):
                if mtd.get('id') == 'jypz':
                    hydm = mtd.string.strip().split('：')[1]
                    logging.info("hydm: %s" % hydm)
                    
        if(m.get('id') == 'ccpmtable'):
            logging.info("processing real data")
            mtr_count = 0
            table_end = False
            for mtr in m.findAll('tr'):
                if table_end == True:
                    break
                mtr_count+=1
                tr_values = []
                if mtr.get('class') == 'rowb':#get all real data
                    logging.info('处理第%s个表，第%s行' % (table_c,mtr_count))
                    for index,mtd in enumerate(mtr.findAll('td')):
##                        print "mtd: %s" % mtd
##                        print "mtd.text: %s" %  mtd.string
##                        print "mtd.content: %s" %  mtd.contents
                        
                        value = mtd.string.strip() if mtd.string else None
                        if value == None:#process 2011 data
                            value = mtd.contents[1].strip() if len(mtd.contents)>1 else None
                        if value == '&nbsp;':
                            value = "blank"
                            #logging.info('blank',)
                        #else:
                            #logging.info(value,)
                        if value.encode('utf-8') == '合计': 
                            table_end = True
                            break
                        tr_values.append(value)      
##                time.sleep(0.1)
                if len(tr_values) > 0:
                    try:
                        conn = None
                        cursor = None
                        conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
                        cursor = conn.cursor()
                        if tr_values[1]!='blank':
                            logging.info(query1 % ('上期',hydm,tr_values[1],'成交量',tr_values[2],url_date))
                            cursor.execute(query1,('上期',hydm,tr_values[1],'成交量',tr_values[2],url_date))
                        if tr_values[5]!='blank':
                            logging.info(query2 % ('上期',hydm,tr_values[5],'持买单量',tr_values[6],url_date))
                            cursor.execute(query2,('上期',hydm,tr_values[5],'持买单量',tr_values[6],url_date))
                        if tr_values[9]!='blank':
                            logging.info(query3 % ('上期',hydm,tr_values[9],'持卖单量',tr_values[10],url_date))
                            cursor.execute(query3,('上期',hydm,tr_values[9],'持卖单量',tr_values[10],url_date))
                    except Exception,e:
                        logging.error(" MySQL server exception!!!")
                        logging.error(e)
                    finally:
                        if cursor!= None:
                            cursor.close()
                        if conn!= None:
                            conn.commit()
                            conn.close()
                    
##        time.sleep(1)
time.sleep(3)            
        


