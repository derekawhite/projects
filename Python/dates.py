from datetime import datetime
from datetime import date, timedelta
import sys

if len(sys.argv) > 2:
    d1s = sys.argv[1]
    d2s = sys.argv[2]

    d1 = datetime.strptime(d1s, '%d/%m/%Y')
    d2 = datetime.strptime(d2s, '%d/%m/%Y')

    thisdate = d2
    end_date = d2.replace(year=d2.year + 2000)
    delta = timedelta(days=1)
    mindiff = -1


    while thisdate <= end_date:
        days1 = (thisdate - d1).days
        days2 = (thisdate - d2).days
        days2rev = int(str(days2)[::-1])
        diff = abs(days2rev - days1)

        if mindiff == -1 or  diff <= mindiff:
            mindiff = diff
            mindate = thisdate.strftime('%d/%m/%Y')
            print ( f"{mindate} {days1} {days2} {days2rev} {mindiff}")

        thisdate += delta
else:
    print("dates <first date> <second date> (dd/mm/yyyy)")
        




