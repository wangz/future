import datetime
import os


if len(sys.argv)==4:
    if sys.argv[1]!=None:
    	where = sys.argv[1]
        url_date1 = sys.argv[2]
        url_date2 = sys.argv[3]
else:
    print "need 3 args ,which ,time from, and time end ,example:shfe 20120912 20120915"
    exit(1)

if where == 'shfe':	
    locate = "./obtain_shfe.py %s"
if where == 'dce':		
    locate = "./obtain_dce.py %s"
if where == 'cffex':
    locate = "./obtain_cffex.py %s"
if where == 'czce':
    locate = "./obtain_czce.py %s"

d1 = datetime.date(url_date1[0:4],url_date1[4:6],url_date1[6:8])

while(d1 < datetime.date(url_date2[0:4],url_date2[4:6],url_date2[6:8])):
    d1 = d1 + datetime.timedelta(1)
    print d1.strftime('%Y%m%d')
    os.system(locate % d1.strftime('%Y%m%d') )
    

