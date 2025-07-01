from bluetooth import *
from itertools import count

def input_and_send():
    while True:
        data = input()
        if len(data) == 0: break
        sock.send(data)
        sock.send("\n")

x = []
y = []
index = count()
def rx_and_echo():
    while True:
        data = sock.recv(buf_size)
        if data:
            d = int(data.decode('utf-8'))
            y.append(d)
        else:
            y.append(0)
        x.append(next(index))
        print(x[-1],y[-1])
            
#MAC address of ESP32
addr = "78:21:84:88:A9:BE"
#uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
#service_matches = find_service( uuid = uuid, address = addr )
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

#input_and_send()
rx_and_echo()

sock.close()
print("\n--- bye ---\n")