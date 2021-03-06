#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
# pip install BeautifulSoup MySQL-python   for old data 
#yum install MySQL-python
import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment
from datetime import * 
import time,logging,MySQLdb
import re
import dbconf

reload(sys) 
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='futures.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG)
      # 中金最少放在1，然后是郑州，2，然后是上海3，然后是大连4
query1 = "insert into tr(og,ct,co,vl,dt) values (%s,%s,%s,%s,%s)"
query2 = "insert into lp(og,ct,co,vl,dt) values (%s,%s,%s,%s,%s)"
query3 = "insert into sp(og,ct,co,vl,dt) values (%s,%s,%s,%s,%s)"




# url_date = "20040713"
url_date = "20091012"

if len(sys.argv)>1:
    if sys.argv[1]!=None:
        url_date = sys.argv[1]
else:
    logging.info('未输入日期,use today')
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
    
    if isinstance(e,urllib2.HTTPError):
        logging.warning("下载此页信息失败 http exception code:%s ,URL：%s" % (e.code,url_one))
        sys.exit(0)
    else:
        logging.error("下载此页信息失败！URL：%s" % url_one)
        logging.error(e)
        sys.exit(1)
finally:
    if f!=None:
        f.close()

# f2=open('data_old.htm','w')
# f2.write(rawdata)
# f2.close()

# f3= open('data_old.htm','r')
# rawdata = f3.read()
# f3.close()

#delete already get data
conn = None
cursor = None
try:
    conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
    cursor = conn.cursor()
    delete_sql = "delete from lp where og='%s' and dt=%s;\
    delete from sp where og='%s' and dt=%s;\
    delete from tr where og='%s' and dt=%s;" 

    check_sql = "select count(*) from lp where og='%s' and dt=%s;"
    
    cursor.execute(check_sql % ('3',url_date))
     
    logging.info("already get data count need delete: %s" %  cursor.fetchall()[0][0])

    cursor.execute(delete_sql % ('3',url_date,'3',url_date,'3',url_date))
    logging.info(delete_sql %  ('上期',url_date,'上期',url_date,'上期',url_date))
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


# cankan:https://gist.github.com/dndn/859717
# replace <!- -> wrong comments
# pattern = re.compile('<\!\-.*\->')
pattern = re.compile('<\!\-[^>]*\->')   #re_comment=re.compile('<!--[^>]*-->')#HTML注释
# pattern = re.compile('<\!\-[\s\S]*\->') 
print "<! -> count:",len(pattern.findall(rawdata))
# print pattern.findall(rawdata)

# f2=open('patern.log','w')
# f2.write(''.join(pattern.findall(rawdata)))
# f2.close()

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

        for index,mtd in enumerate(m.findAll('td')):  
            if index == 0:#first td,if is 交易品种 then get it ;else processing
                value = mtd.string
                if value == None:
                    value = mtd.find('div') #for 2007
                    if value != None:
                        value = value.string
                        if value != None:#for 2012 has div but none
                            value = value.strip()
                        else:
                            for mmtd in m.findAll('td'):
                                if mmtd.get('id') == 'jypz':
                                    value = mmtd.string.strip()
                    else:
                        for mmtd in m.findAll('td'):#for 2012
                            if mmtd.get('id') == 'jypz':
                                value = mmtd.string.strip()
                else:
                    value = value.strip()
                if value == None:
                    continue
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
                                    logging.info(query1 % ('3',hydm,tr_values[1],tr_values[2],url_date))
                                    cursor.execute(query1,('3',hydm,tr_values[1],tr_values[2],url_date))
                                if tr_values[5]!='blank':
                                    logging.info(query2 % ('3',hydm,tr_values[5],tr_values[6],url_date))
                                    cursor.execute(query2,('3',hydm,tr_values[5],tr_values[6],url_date))
                                if tr_values[9]!='blank':
                                    logging.info(query3 % ('3',hydm,tr_values[9],tr_values[10],url_date))
                                    cursor.execute(query3,('3',hydm,tr_values[9],tr_values[10],url_date))
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
                break
                    
#        time.sleep(1)
time.sleep(3)            
from smtpmail import send_mail
send_mail(["51649548@qq.com"],"上期持仓提取情况","%s数据 日期%s 提取完成" % ('上期',url_date))
send_mail(["aaronfu@triumphantbank.com"],"上期持仓提取情况","%s数据 日期%s 提取完成" % ('上期',url_date))
send_mail(["johlu@triumphantbank.com"],"上期持仓提取情况","%s数据 日期%s 提取完成" % ('上期',url_date))
send_mail(["dangwannian@triumphantbank"],"上期持仓提取情况","%s数据 日期%s 提取完成" % ('上期',url_date))       


