import pydbus

bus = pydbus.SystemBus()

adapter = bus.get('org.bluez', '/org/bluez/hci0')
mngr = bus.get('org.bluez', '/')

def list_connected_devices():
    global addr
    mngd_objs = mngr.GetManagedObjects()
    for path in mngd_objs:
        con_state = mngd_objs[path].get('org.bluez.Device1', {}).get('Connected', False)
        if con_state:
            addr = mngd_objs[path].get('org.bluez.Device1', {}).get('Address')
            
if __name__ == '__main__':
    list_connected_devices()
try: 
    print(addr)
except:
    addr = 0
    print(addr)