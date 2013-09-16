import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment

f3= open('test.htm','r')
rawdata = f3.read()
f3.close()
print rawdata
soup = BeautifulSoup(rawdata)
for m in soup.findAll('table'):
    time.sleep(2)
    if m.get('id')== 'cct':    
        for mtd in m.findAll('td'):
             print mtd.string
##    print m.findAll('td')
