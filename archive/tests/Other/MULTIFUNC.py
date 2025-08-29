from bluetooth import *
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
plt.style.use('fivethirtyeight')

def rx_and_echo():
    while True:
        data = sock.recv(buf_size)
        if data:
            x.append(next(index))
            y.append(int(data.decode('utf-8')))
        
def plot(i):
    try:
        plt.cla()
        plt.plot(x,y)
    except:
        plot(1)
    
def animation():
    ani = FuncAnimation(plt.gcf(), plot, interval = 20)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    with Manager() as manager:
        index = count()
        x = manager.list([])
        y = manager.list([])
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
        p1 = Process(target = rx_and_echo)
        p2 = Process(target = animation)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
    
sock.close()