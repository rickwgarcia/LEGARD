from bluetooth import *
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process
        
def rx_and_echo():
    while True:
        data = sock.recv(buf_size)
        if data:
            y.append(int(data.decode('utf-8')))
        else:
            y.append(0)
        x.append(next(index))
        print(x[-1],y[-1])
        
#MAC address of ESP32
addr = "78:21:84:88:A9:BE"
service_matches = find_service( address = addr )

buf_size = 1024;

if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)
    
first_match = service_matches[0]
name = first_match["name"]
host = first_match["host"]

port=1
print("connecting to \"%s\" on %s, port %s" % (name, host, port))

# Create the client socket
sock=BluetoothSocket(RFCOMM)
sock.connect((host, port))

print("connected")

if __name__ == "__main__":
    
    plt.figure()
    plt.style.use('fivethirtyeight')
    x = []
    y = []
    index = count()
    p1 = Process(target = rx_and_echo).start()
    def ani(i):
        plt.cla()
        plt.plot(x,y)
        print("YES"+x,y)
    ani = FuncAnimation(plt.gcf(), ani)
    plt.tight_layout()
    plt.show()
sock.close()
