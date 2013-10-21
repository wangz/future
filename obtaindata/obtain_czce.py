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
if url_date>"20100824":
    url_one = "http://www.czce.com.cn/portal/exchange/%s/datatradeholding/%s.htm" % (url_date[0:4],url_date)
else:
    url_one = "http://www.czce.com.cn/portal/exchange/jyxx/pm/pm%s.html" %  url_date
logging.info("URL：%s" % url_one)

try:
    f = None
    f = urllib2.urlopen(url_one)
    rawdata = f.read()
except Exception,e:
    if isinstance(e,urllib2.HTTPError):
        logging.warning("此页可能无信息 http exception code:%s ,URL：%s" % (e.code,url_one))
        sys.exit(0)
    else:
        logging.error("下载此页信息失败！URL：%s" % url_one)
        logging.error(e)
        sys.exit(1)
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

    check_sql = "select count(*) from data_buy where origin='%s' and pub_date='%s';"
    cursor.execute(check_sql %  ('郑州',url_date))
    logging.info("already get data count need delete:%s" %  cursor.fetchall()[0][0])

    conn.commit()

    cursor.execute(delete_sql %  ('郑州',url_date,'郑州',url_date,'郑州',url_date))
    logging.info(delete_sql %  ('郑州',url_date,'郑州',url_date,'郑州',url_date))
except Exception,e:
    logging.error(" MySQL server exception while delete sql!!!")
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
    if url_date>"20100824":
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
    else:
        print url_date
        for div_index,m in enumerate(soup.findAll('div',align="left")): 
            hydm = None
            hydm = m.find('b').find('font').string
            if hydm.find('合约')!= -1:
                hydm = hydm.split(':')[0]
                hydm=hydm.replace('合约代码','')
                hydm=hydm.replace('日期','').strip()
                print hydm
                if hydm!=None:
                    tt = m.nextSibling
                    if tt.name == "table":
                        for t_index,tr_t in enumerate(tt.findAll('tr')):
                            logging.info("hang:%s" % t_index)
                            if t_index == 0:
                                continue
                            else:
                                tr_values = []
                                for td_index,mtd in enumerate(tr_t.findAll('td')):
                                    value = mtd.string
                                    if value == None:
                                        break
                                    else:
                                        value = value.strip()
                                    if value == '合计':
                                        break
                                    value = value.replace(',','')
                                    if value == '-':
                                        value = 'blank'
                                    tr_values.append(value)
                                if len(tr_values)>0 and hydm!=None:
                                    # put into database
                                    # time.sleep(1)
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
        


