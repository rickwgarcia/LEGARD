#import subprocess

#subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
from bluetooth import *
import time
import pydbus

bus = pydbus.SystemBus()

adapter = bus.get('org.bluez', '/org/bluez/hci0')
mngr = bus.get('org.bluez', '/')

def list_connected_devices():
    global addrs
    mngd_objs = mngr.GetManagedObjects()
    for path in mngd_objs:
        con_state = mngd_objs[path].get('org.bluez.Device1', {}).get('Connected', False)
        if con_state:
            addrs = mngd_objs[path].get('org.bluez.Device1', {}).get('Address')
            
if __name__ == '__main__':
    list_connected_devices()

try:
    addr = addrs
except:
    addr = 0
    
if addr != 0:
    matches = find_service(address = addr)

    buf_size = 1024
    service_matches = find_service(address = addr)
    first_match = service_matches[0]

    port = 1
    host = first_match["host"]
    sock = BluetoothSocket(RFCOMM)
    sock.connect((host, port))

    while True:
        sock.send("hello!!")
        print('info sent')
        time.sleep(1)
        
sock.close()

