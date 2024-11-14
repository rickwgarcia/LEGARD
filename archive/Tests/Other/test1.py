import os
import datetime
t = ['admin']
current_time = datetime.datetime.now()
current_day = datetime.date.today()
today = str(current_day) + ' ' +str(current_time.hour) + ':' + str(current_time.minute)

os.mkdir("Users/"+t[-1]+"/"+today)