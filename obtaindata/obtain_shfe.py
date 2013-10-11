#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
# pip install BeautifulSoup MySQL-python   for old data 
import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment
from datetime import * 
import time,logging,MySQLdb
import re
import dbconf

reload(sys) 
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='future_shfe_all.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG)
 
query1 = "insert into data_trading(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query2 = "insert into data_buy(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"
query3 = "insert into data_selling(origin,contract,company,value_type,real_value,pub_date) values (%s,%s,%s,%s,%s,%s)"

# url_date = "20040713"
url_date = "20091012"

if len(sys.argv)>1:
    if sys.argv[1]!=None:
        url_date = sys.argv[1]
else:
    logging.info('未输入日期')
    exit(1)
    # now = date.today()
    # url_date = now.strftime('%Y%m%d')
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

f2=open('data_old.htm','w')
f2.write(rawdata)
f2.close()

# f3= open('data_old.htm','r')
# rawdata = f3.read()
# f3.close()

# replace <!- -> wrong comments
pattern = re.compile('<\!\-.*\->')
print pattern.findall(rawdata)
rawdata = pattern.sub('',rawdata)

ishasdata = False
logging.info("处理URL为：%s" % url_one)
table_c = 0

soup = BeautifulSoup(rawdata)
#value has comment,then cannot parse!!!so extract it
comments = soup.findAll(text=lambda text:isinstance(text, Comment))
print "comments len: %d " % len(comments)
[comment.extract() for comment in comments]

##f2=open('data_20110311_b.htm','w')
##f2.write(soup)
##f2.close()

# styles = soup.findAll('style')
# print "style len: %d " % len(styles)
# [style.extract() for style in styles]


for m in soup.findAll('table'):
    table_c+=1
logging.info( "find table count = %s" % table_c)

if table_c > 3:
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

        for index,mtd in enumerate(m.findAll('td')):  
            if index == 0:#first td,if is 交易品种 then get it ;else processing
                value = mtd.string
                if value == None:
                    value = mtd.find('div').string.strip()
                else:
                    value = value.strip()
                if value.find('交易品种')!=-1 or value.find('合约代码')!=-1:
                    if value.find(':')!=-1:
                        hydm = value.split(':')[1] 
                    if value.find('：')!=-1:
                        hydm = value.split('：')[1] 
                    logging.info("hydm: %s" % hydm)  
                    continue 
                if value.find('会员类别')!=-1:
                    continue               
                else:
                    print hydm
                    logging.info("processing real data")                                      
                    mtr_count = 0
                    table_end = False
                    for mtr in m.findAll('tr'):
                        if table_end == True:
                            break
                        mtr_count+=1
                        tr_values = []

                        logging.info('处理第%s个表，第%s行' % (table_c,mtr_count))
                        if mtr_count == 1:
                            continue
                        for index,mtd in enumerate(mtr.findAll('td')):
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
            else:
                break
                    
#        time.sleep(1)
time.sleep(3)            
        


