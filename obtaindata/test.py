import sys,re,urllib2,urllib,cookielib,chardet,time
from BeautifulSoup import BeautifulSoup,Comment

f3= open('test.htm','r')
rawdata = f3.read()
f3.close()
print rawdata
soup = BeautifulSoup(rawdata)
for m in soup.findAll('table'):
##    time.sleep(2)
    if m.get('id')== 'cct':    
        for mtd in m.findAll('td'):
             print mtd.string
##    print m.findAll('td')

soup2 = BeautifulSoup('''<td class="a1" align="right">
^M
                        ^M
                        ^M
                        ^M
                        315^M
                        ^M
                       ^M
                        </td>

''')
print soup2.find('td').string
for index,mtd in enumerate(soup2.findAll('td')):
    print "mtd: %s" % mtd
    print "mtd.text: %s" %  mtd.string

