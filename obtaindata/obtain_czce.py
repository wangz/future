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

logging.basicConfig(filename='future_czce.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG)
# console = logging.StreamHandler();
# console.setLevel(logging.INFO);
# # set a format which is simpler for console use
# formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s');
# # tell the handler to use this format
# console.setFormatter(formatter);
# logging.getLogger('').addHandler(console);

query1 = "insert into data_trading(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query2 = "insert into data_buy(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query3 = "insert into data_selling(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"

url_date = "20130711"
print len(sys.argv)
if len(sys.argv)>1:
    if sys.argv[1]!=None:
        url_date = sys.argv[1]
else:
    logging.info("未输入日期，则默认处理当前数据!")
    now = date.today()
    url_date = now.strftime('%Y%m%d')
logging.info("处理日期 url_date: %s",url_date)
'''obtain futures data'''
url_one = "http://www.czce.com.cn/portal/exchange/%s/datatradeholding/%s.htm" % (url_date[0:4],url_date)

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

# f2=open('data_czce_20130711.htm','w')
# f2.write(rawdata)
# f2.close()

# f3= open('data_czce_20130711.htm','r')
# rawdata = f3.read()
# f3.close()

#delete already get data
conn = None
cursor = None
try:
    conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
    cursor = conn.cursor()
    delete_sql = "delete from data_buy where origin='%s' and pub_date=%s;\
    delete from data_selling where origin='%s' and pub_date=%s;\
    delete from data_trading where origin='%s' and pub_date=%s;" 

    check_sql = "select count(*) from data_buy where origin='%s' and pub_date=%s;"
    
    cursor.execute(check_sql % ('郑州',url_date))
    print 
    logging.info("already get data count need delete:" %  cursor.fetchall()[0][0])

    cursor.execute(delete_sql % ('郑州',url_date,'郑州',url_date,'郑州',url_date))
    logging.info(delete_sql %  ('郑州',url_date,'郑州',url_date,'郑州',url_date))
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
table_c = 0

soup = BeautifulSoup(rawdata)
#value has comment,then cannot parse!!!so extract it
comments = soup.findAll(text=lambda text:isinstance(text, Comment))
[comment.extract() for comment in comments]


for m in soup.findAll('table'):
    table_c+=1
logging.info( "find table count = %s" % table_c)

if table_c > 3:
    ishasdata = True
    logging.info("obtain data success,start process")
else:
    logging.warning("此页未找到足够数据！obtain data failed date: %s" % url_one)

if ishasdata:
    
    for table_index,m in enumerate(soup.findAll('table')): 
        hydm = 'None' #heyuedaima  
        if m.get('class') != 'table':
            continue
        for tr_index,mtr in enumerate(m.findAll('tr')):
            if tr_index == 0 :
                if mtr.find('td'):
                    hydm = mtr.find('td').find('b').string.split('&nbsp;')[0]
                    if hydm.find('合约')!= -1:
                        hydm = hydm.split('：')[1]
                    else:
                        break
            elif tr_index > 1:
                tr_values = []
                for td_index,mtd in enumerate(mtr.findAll('td')):
                    value = mtd.string
                    if value == '合计':
                        break
                    value = value.replace(',','')
                    if value == '-':
                        value = 'blank'
                    tr_values.append(value)
                if len(tr_values)>0 and hydm!=None:
                    # put into database
                    try:
                        conn = None
                        cursor = None
                        conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
                        cursor = conn.cursor()
                        if tr_values[1]!='blank':
                            logging.info(query1 % ('郑州',hydm,tr_values[1],'成交量',tr_values[2],url_date))
                            cursor.execute(query1,('郑州',hydm,tr_values[1],'成交量',tr_values[2],url_date))
                        if tr_values[5]!='blank':
                            logging.info(query2 % ('郑州',hydm,tr_values[4],'持买单量',tr_values[5],url_date))
                            cursor.execute(query2,('郑州',hydm,tr_values[4],'持买单量',tr_values[5],url_date))
                        if tr_values[9]!='blank':
                            logging.info(query3 % ('郑州',hydm,tr_values[7],'持卖单量',tr_values[8],url_date))
                            cursor.execute(query3,('郑州',hydm,tr_values[7],'持卖单量',tr_values[8],url_date))
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

            # time.sleep(1)

time.sleep(3)            
        


