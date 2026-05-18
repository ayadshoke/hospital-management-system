import datetime as dt
from datetime import date
import calendar
# x= dt.datetime.now().day
# x= dt.datetime.date()
# x= dt.datetime.now().weekday()+3
# x= dt.datetime.now().month
# x= dt.datetime.now().year
# x= dt.datetime.now().isoweekday()
# x= dt.date.today().isoformat()
# x= dt.date.today()
# d = x.strftime('%A')
# m =dt.time.minute
# d = dt.date(2026,1,5)

# print(x)

# mm =(1,'ayad')
# nn = mm,
# print(type(mm))
# yy = range(nn)
# cal = calendar.monthrange(2025,1)
# print(cal)
# amount =70.75
# p = amount*100 % 100
# print(p)
day = dt.datetime.now().today().weekday()+1
print(day)
