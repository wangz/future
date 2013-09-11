#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
# pip install BeautifulSoup
import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment
'''obtain futures data'''

##url_one = "http://www.shfe.com.cn/dailydata/kx/pm20130711.html"
##f = urllib2.urlopen(url_one)
##rawdata = f.read()
##f2=open('data.htm','w')
##f2.write(rawdata)
##f2.close()

f3= open('data.htm','r')
rawdata = f3.read()
f3.close()
table_c = 0
ishasdata = False
rawdata = BeautifulSoup(rawdata).prettify()
soup = BeautifulSoup(rawdata)
#value has comment,then cannot parse!!!so extract it
comments = soup.findAll(text=lambda text:isinstance(text, Comment))
[comment.extract() for comment in comments]

for m in soup.findAll('table'):
    table_c+=1
print "find table count = %s" % table_c
if table_c > 5:
    ishasdata = True
    print "obtain data success,start process"
else:
    print "obtain data failed"

if ishasdata:
    table_c = 0
    jypz = None #heyuedaima
    for m in soup.findAll('table'):   
        table_c+=1
        print 'processing table: %d' % table_c
        if(m.get('id') == None):
            for mtd in m.findAll('td'):
                if mtd.get('id') == 'jypz':
                    #td_temp = mtd.extract()#very fast
##                    print td.string #too slow
                    jypz = mtd.string
                    print jypz
                    
        if(m.get('id') == 'ccpmtable'):
            print 'process real data...'
            mtr_count = 0
            for mtr in m.findAll('tr'):
                #tr_temp = mtr.extract()
                mtr_count+=1
                if mtr.get('class') == 'rowb':
                    print '处理第%s个表，第%s行' % (table_c,mtr_count)
                    for mtd in mtr.findAll('td'):
                        #mtd_temp = mtd.extract()
##                        print mtd_temp
                        value = mtd.string.strip() if mtd.string else None
                        print value,
                        if value.encode('utf-8') == '合计': 
                            break
                    print ''       
                time.sleep(0.1)
        time.sleep(1)
            
        
#not use SoupStrainer,and use extract instand 		
##            for td in SoupStrainer('td'):
##                print td
##                if td.get('id') == 'jypz':
##                    print td.string 
        


