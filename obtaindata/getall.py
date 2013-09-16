import datetime
import os

d = datetime.date(2002,2,5)
print d
while(d < datetime.date(2013,9,18)):
    d = d + datetime.timedelta(1)
    print d.strftime('%Y%m%d')
    os.system("./obtain.py %s" % d.strftime('%Y%m%d') )
    
