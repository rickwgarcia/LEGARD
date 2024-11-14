import time

t0 = time.time()

time.sleep(2)

t1 = time.time()

#total = t1-t0

print(t0+2)
print(t1)

# Python3 code to demonstrate 
# attributes of now() 
    
# importing datetime module for now() 
import datetime
    
# using now() to get current time 
current_time = datetime.datetime.now()
current_day = datetime.date.today() 
print ("Today : ", end = "") 
print (str(current_day) + ' ' +str(current_time.hour) + ':' + str(current_time.minute))