#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
import urllib,urllib2,sys
from BeautifulSoup import BeautifulSoup,Comment
from datetime import * 
import time,logging,MySQLdb
import re
import dbconf

reload(sys) 
sys.setdefaultencoding('utf8')

def post(url, data):  
    req = urllib2.Request(url)  
    data = urllib.urlencode(data,True)  
    #enable cookie  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read() 

def getcontract(trade_date = None,variety = None):
    #'20130918'

    posturl = "http://www.dce.com.cn/PublicWeb/MainServlet"  
    data = {'action':'Pu00021_contract', 'Pu00021_Input.trade_date':trade_date,'Pu00021_Input.content':'0','Pu00021_Input.content':'1', 'Pu00021_Input.content':['0','1','2'], 'Pu00021_Input.variety':variety,'Pu00021_Input.trade_type':'0'}  
    
    rawdata = post(posturl, data)

    rawdata = unicode(rawdata,encoding='gbk').encode('utf-8')
    # print rawdata 
    soup = BeautifulSoup(rawdata)
    contracts = []
    for m in soup.findAll('table'):
        if m.get('class') == 'table':
            for i in m.findAll('input'):
                if i.get('type') == 'radio':
                	contracts.append(i.get('value'))
    return contracts

def main(): 
    logging.basicConfig(filename='future_dce.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG)
     
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
        
        cursor.execute(check_sql % ('大连',url_date))
        logging.info("already get data count need delete: %s" %  cursor.fetchall()[0][0])

        cursor.execute(delete_sql % ('大连',url_date,'大连',url_date,'大连',url_date))
        logging.info(delete_sql %  ('大连',url_date,'大连',url_date,'大连',url_date))
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

    varietys = ['a','b','c','j','jm','l','m','p','v','y','s']
    for v in varietys:
        print v
        try:
            contracts = getcontract(variety=v,trade_date=url_date)
        except Exception,e:
            logging.error(" get page data failed!!!")
            logging.error(e)
            sys.exit(1)

        print contracts
        if len(contracts)>0:
            posturl = "http://www.dce.com.cn/PublicWeb/MainServlet"
            for c in contracts:                  
                data = {'action':'Pu00021_result', 'Pu00021_Input.trade_date':url_date,'Pu00021_Input.content':'0','Pu00021_Input.content':'1', 'Pu00021_Input.content':['0','1','2'], 'Pu00021_Input.variety':v,'Pu00021_Input.trade_type':'0','Pu00021_Input.contract_id':c}  
                rawdata = post(posturl, data)
                rawdata = unicode(rawdata,encoding='gbk').encode('utf-8')

                soup = BeautifulSoup(rawdata)
                for t in soup.findAll('table'):
                    for index,r in enumerate(t.findAll('tr')):
                        tr_values = []
                        if index == 0:
                            if r.get('class') == 'tr0':
                                continue
                            else:
                                break
                        else:
                            for d in r.findAll('td'):
                                value = d.string.strip() if d.string else None
                                if value == '&nbsp;':
                                    value = "blank"
                                if value.encode('utf-8') == '总计': 
                                    break
                                # print value
                                value = value.replace(',','')
                                tr_values.append(value)
                        if len(tr_values) > 0:
                            try:
                                conn = None
                                cursor = None
                                conn = MySQLdb.Connection(dbconf.host, dbconf.user, dbconf.password, dbconf.dbname,charset='utf8')
                                cursor = conn.cursor()
                                if tr_values[1]!='blank':
                                    logging.info(query1 % ('大连',c,tr_values[1],'成交量',tr_values[2],url_date))
                                    cursor.execute(query1,('大连',c,tr_values[1],'成交量',tr_values[2],url_date))
                                if tr_values[5]!='blank':
                                    logging.info(query2 % ('大连',c,tr_values[5],'持买单量',tr_values[6],url_date))
                                    cursor.execute(query2,('大连',c,tr_values[5],'持买单量',tr_values[6],url_date))
                                if tr_values[9]!='blank':
                                    logging.info(query3 % ('大连',c,tr_values[9],'持卖单量',tr_values[10],url_date))
                                    cursor.execute(query3,('大连',c,tr_values[9],'持卖单量',tr_values[10],url_date))
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

            time.sleep(0.5)
                # rawdata = unicode(rawdata,encoding='gbk').encode('utf-8')

#action=Pu00021_result&Pu00021_Input.prefix=&Pu00021_Input.trade_date=20130924&Pu00021_Input.content=0&Pu00021_Input.content=1&Pu00021_Input.content=2&Pu00021_Input.variety=a&Pu00021_Input.trade_type=0&Pu00021_Input.contract_id=a1311&Submit=%B2%E9+%D1%AF

#Referer	http://www.dce.com.cn/PublicWeb/MainServlet?action=Pu00021_search
#action=Pu00021_result&Pu00021_Input.prefix=&Pu00021_Input.trade_date=20130918&Pu00021_Input.content=0&Pu00021_Input.content=1&Pu00021_Input.content=2&Pu00021_Input.variety=y&Pu00021_Input.trade_type=0&Pu00021_Input.contract_id=y1311&Submit=%B2%E9+%D1%AF
# <option value="a">豆一</option>
# <option value="b">豆二</option>
# <option value="c">玉米</option>
# <option value="j">焦炭</option>
# <option value="jm">焦煤</option>
# <option value="l">聚乙烯</option>
# <option value="m">豆粕</option>
# <option value="p">棕榈油</option>
# <option value="v">聚氯乙烯</option>
# <option value="y">豆油</option>
# <option value="s">大豆</option>

    

#action=Pu00021_contract&Pu00021_Input.prefix=&Pu00021_Input.trade_date=20130918&Pu00021_Input.content=0&Pu00021_Input.content=1&Pu00021_Input.content=2&Pu00021_Input.variety=a&Pu00021_Input.trade_type=0&Pu00021_Input.contract_id=
if __name__ == '__main__':  
    main()