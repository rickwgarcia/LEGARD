from bluetooth import *
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process

plt.style.use('fivethirtyeight')
x = []
y = []
index = count()

def input_and_send():
    while True:
        data = input()
        if len(data) == 0: break
        sock.send(data)
        sock.send("\n")
        
def rx_and_echo(i):
   # while True:
    data = sock.recv(buf_size)
    if data:
        y.append(int(data.decode('utf-8')))
    else:
        y.append(0)
    x.append(next(index))
    print(x[-1],y[-1])
    plt.cla()
    plt.plot(x,y)
        

#MAC address of ESP32
addr = "78:21:84:88:A9:BE"
service_matches = find_service( address = addr )

buf_size = 1024;

if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)

for s in range(len(service_matches)):
    print("\nservice_matches: [" + str(s) + "]:")
    print(service_matches[s])
    
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

port=1
print("connecting to \"%s\" on %s, port %s" % (name, host, port))

# Create the client socket
sock=BluetoothSocket(RFCOMM)
sock.connect((host, port))

print("connected")
    
ani = FuncAnimation(plt.gcf(), rx_and_echo)
plt.tight_layout()
plt.show()
sock.close()
